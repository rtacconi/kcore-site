(function (root) {
  var HCL_KW = { resource: 1, data: 1, variable: 1, output: 1, module: 1, provider: 1, terraform: 1, locals: 1, for: 1, in: 1, if: 1 };
  var NIX_KW = { let: 1, in: 1, inherit: 1, if: 1, then: 1, else: 1, with: 1, rec: 1, assert: 1, or: 1 };
  var BOOL = { true: 1, false: 1, null: 1, yes: 1, no: 1 };

  function looksLikeTable(text) {
    var lines = text.split("\n").filter(function (l) { return l.trim(); });
    if (lines.length < 2) return false;
    var spaced = 0;
    for (var i = 0; i < lines.length; i++) {
      if (/\S\s{2,}\S/.test(lines[i])) spaced++;
    }
    if (spaced < lines.length - 1) return false;
    return !/(--|:\s|=\s|^\s*#|\{|\})/m.test(text);
  }

  function langOf(el) {
    var node = el;
    while (node) {
      if (node.classList) {
        if (node.classList.contains("docs-tf-only")) return "hcl";
        if (node.classList.contains("docs-yaml-only")) return "yaml";
        if (node.classList.contains("docs-cli-only")) return "shell";
      }
      node = node.parentElement;
    }
    return langOfText(el.textContent || "");
  }

  function langOfText(text) {
    var lines = text.split("\n");
    var sample = "";
    for (var i = 0; i < lines.length; i++) {
      var s = lines[i].trim();
      if (!s || s.charAt(0) === "#") continue;
      sample = s;
      break;
    }
    if (!sample) return "shell";
    if (/^(resource|terraform|provider|variable|output|module|data|locals)\b/.test(sample)) return "hcl";
    if (/^(apiVersion|kind:|diskLayout:|storage:|webhooks:|metadata:|spec:)/.test(sample)) return "yaml";
    if (/^[A-Za-z0-9_."'-]+\s*:/.test(sample)) return "yaml";
    if (sample.charAt(0) === "{" || /^(let|with)\b/.test(sample)) return "nix";
    return "shell";
  }

  function push(out, type, text) {
    if (!text) return;
    var last = out[out.length - 1];
    if (last && last.type === type) last.text += text;
    else out.push({ type: type, text: text });
  }

  function readString(line, i, quote) {
    var j = i + 1;
    while (j < line.length) {
      if (line.charAt(j) === "\\") { j += 2; continue; }
      if (line.charAt(j) === quote) return j + 1;
      j++;
    }
    return line.length;
  }

  function readNumber(line, i) {
    var j = i;
    while (j < line.length && /[0-9]/.test(line.charAt(j))) j++;
    if (line.charAt(j) === "." && /[0-9]/.test(line.charAt(j + 1))) {
      j++;
      while (j < line.length && /[0-9]/.test(line.charAt(j))) j++;
      while (line.charAt(j) === "." && /[0-9]/.test(line.charAt(j + 1))) {
        j++;
        while (j < line.length && /[0-9]/.test(line.charAt(j))) j++;
      }
    }
    return j;
  }

  function tokenizeLine(line, lang, commandSeen) {
    var out = [];
    var i = 0;
    while (i < line.length) {
      var c = line.charAt(i);
      if (c === "#" || (lang === "hcl" && line.substr(i, 2) === "//")) {
        push(out, "code-comment", line.slice(i));
        break;
      }
      if (lang === "nix" && c === "'" && line.charAt(i + 1) === "'") {
        var k = line.indexOf("''", i + 2);
        var end = k === -1 ? line.length : k + 2;
        push(out, "code-string", line.slice(i, end));
        i = end;
        continue;
      }
      if (c === '"' || c === "'") {
        var endQ = readString(line, i, c);
        push(out, "code-string", line.slice(i, endQ));
        i = endQ;
        continue;
      }
      if (lang === "shell" && (c === "|" || (c === "&" && line.charAt(i + 1) === "&") || c === ";")) {
        var op = c === "&" ? "&&" : c;
        push(out, "", op);
        i += op.length;
        commandSeen = false;
        continue;
      }
      if (lang === "shell" && c === "-" && line.charAt(i + 1) === "-" && /[A-Za-z0-9]/.test(line.charAt(i + 2))) {
        var j = i + 2;
        while (j < line.length && /[\w-]/.test(line.charAt(j))) j++;
        push(out, "code-flag", line.slice(i, j));
        i = j;
        continue;
      }
      if (lang === "shell" && c === "-" && /[A-Za-z]/.test(line.charAt(i + 1)) && (i === 0 || /\s/.test(line.charAt(i - 1)))) {
        push(out, "code-flag", line.substr(i, 2));
        i += 2;
        continue;
      }
      if (/[0-9]/.test(c) && (i === 0 || !/[A-Za-z0-9_\-]/.test(line.charAt(i - 1)))) {
        var jn = readNumber(line, i);
        push(out, "code-number", line.slice(i, jn));
        i = jn;
        continue;
      }
      if (lang === "yaml") {
        var indentOk = line.slice(0, i).trim() === "" || line.slice(0, i).trim() === "-" || /-\s+$/.test(line.slice(0, i));
        if (indentOk) {
          var m = line.slice(i).match(/^([A-Za-z_][A-Za-z0-9_.-]*)(\s*:)/);
          if (m) {
            push(out, "code-property", m[1]);
            push(out, "", m[2]);
            i += m[1].length + m[2].length;
            continue;
          }
        }
        var jb = i;
        while (jb < line.length && /[A-Za-z]/.test(line.charAt(jb))) jb++;
        if (jb > i) {
          var word = line.slice(i, jb);
          if (BOOL[word] && (jb === line.length || /[\s,]/.test(line.charAt(jb)))) {
            push(out, "code-number", word);
            i = jb;
            continue;
          }
        }
      }
      if (lang === "hcl" || lang === "nix") {
        if (/[A-Za-z_]/.test(c)) {
          var jw = i + 1;
          while (jw < line.length && /[A-Za-z0-9_-]/.test(line.charAt(jw))) jw++;
          var word2 = line.slice(i, jw);
          var kw = lang === "hcl" ? HCL_KW : NIX_KW;
          var after = /^\s*=/.test(line.slice(jw));
          if (kw[word2]) push(out, "code-keyword", word2);
          else if (after) push(out, "code-property", word2);
          else if (word2 === "true" || word2 === "false" || word2 === "null") push(out, "code-number", word2);
          else push(out, "", word2);
          i = jw;
          continue;
        }
      }
      if (lang === "shell" && /[A-Za-z_./]/.test(c) && !commandSeen && (i === 0 || /\s/.test(line.charAt(i - 1)))) {
        var jc = i + 1;
        while (jc < line.length && /[A-Za-z0-9_.:\/-]/.test(line.charAt(jc))) jc++;
        push(out, "code-keyword", line.slice(i, jc));
        commandSeen = true;
        i = jc;
        continue;
      }
      push(out, "", c);
      i++;
    }
    return { tokens: out, commandSeen: /\\$/.test(line.trim()) };
  }

  function tokenizeBlock(text, lang) {
    if (looksLikeTable(text)) lang = "plain";
    var lines = text.split("\n");
    var commandSeen = false;
    var painted = [];
    for (var i = 0; i < lines.length; i++) {
      var res = tokenizeLine(lines[i], lang, commandSeen);
      commandSeen = lang === "shell" && res.commandSeen;
      painted.push(res.tokens);
    }
    return painted;
  }

  function joinTokens(tokens) {
    var s = "";
    for (var i = 0; i < tokens.length; i++) s += tokens[i].text;
    return s;
  }

  function paint(el) {
    if (el.querySelector && el.querySelector("span")) return;
    var text = el.textContent || "";
    if (!text.trim()) return;
    var lang = langOf(el);
    if (looksLikeTable(text)) return;
    var lines = text.split("\n");
    var commandSeen = false;
    var frag = root.document.createDocumentFragment();
    for (var li = 0; li < lines.length; li++) {
      if (li) frag.appendChild(root.document.createTextNode("\n"));
      var res = tokenizeLine(lines[li], lang, commandSeen);
      commandSeen = lang === "shell" && res.commandSeen;
      for (var t = 0; t < res.tokens.length; t++) {
        var tok = res.tokens[t];
        if (!tok.type) {
          frag.appendChild(root.document.createTextNode(tok.text));
        } else {
          var span = root.document.createElement("span");
          span.className = tok.type;
          span.textContent = tok.text;
          frag.appendChild(span);
        }
      }
    }
    el.textContent = "";
    el.appendChild(frag);
  }

  function install() {
    var nodes = root.document.querySelectorAll("pre code");
    for (var i = 0; i < nodes.length; i++) paint(nodes[i]);
  }

  if (root.document) {
    if (root.document.readyState === "loading") root.document.addEventListener("DOMContentLoaded", install);
    else install();
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { tokenizeBlock: tokenizeBlock, langOfText: langOfText, looksLikeTable: looksLikeTable, joinTokens: joinTokens };
  }
})(typeof window !== "undefined" ? window : globalThis);
