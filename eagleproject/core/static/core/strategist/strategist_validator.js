const strategistValidator = (function () {
  const ethers = window.ethers;
  const iVault = new ethers.utils.Interface(abiVault.abi);
  const iVaultValueChecker = new ethers.utils.Interface(
    abiVaultValueChecker.abi
  );

  let masterEl = undefined;
  let textareaEl = undefined;

  // Constants
  const CONTRACT_NAMES = {
    "0x5e3646A1Db86993f73E6b74A57D8640B69F7e259": "AAVE Strat",
    "0x9c459eeb3FA179a40329b81C1635525e9A0Ef094": "Compound Strat",
    "0xEA2Ef2e2E5A749D4A66b41Db9aD85a38Aa264cb3": "Convex Strat",

    "0x6B175474E89094C44Da98b954EedeAC495271d0F": "DAI",
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "USDC",
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": "USDT",
  };

  const DECIMALS = {
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": 18, //'DAI',
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": 6, //'USDC',
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": 6, //'USDT',
  };

  const MULTI_SEND_ADDRESS = "0x40a2accbd92bca938b02010e17a5b8929b49130d";
  const VAULT = "0xE75D77B1865Ae93c7eaa3040B038D7aA7BC02F70";
  const CHECKER = "0x5B98B3255522E95f842967723Ee4Cc7dCEaa9150";

  // App hooks up to events
  function app(opts) {
    masterEl = opts.masterEl;
    textareaEl = opts.textareaEl;
    textareaEl.onchange = () => {
      setTimeout(refresh, 5);
    };
    textareaEl.onpaste = () => {
      setTimeout(refresh, 5);
    };
    textareaEl.onkeyup = () => {
      setTimeout(refresh, 5);
    };
    refresh();
  }

  // Redraw the output
  function refresh() {
    masterEl.innerHTML = ""; // Clear

    // Data in
    const data = textareaEl.value;

    if (data == "") {
      masterEl.appendChild(element("p", "Awaiting..."));
      return;
    }

    if (data.startsWith("0x8d80ff0a")) {
      masterEl.appendChild(element("h3", "🤹🏻 Multisend"));
      for (const innerTx of parseMultisend(data.slice(10))) {
        const innerEl = parseAndDisplayTx(innerTx.to, innerTx.data);
        masterEl.appendChild(innerEl);
      }
    } else {
      try {
        iVault.parseTransaction({ data: data });
        masterEl.appendChild(parseAndDisplayTx(VAULT, data));
      } catch {
        masterEl.appendChild(parseAndDisplayTx(CHECKER, data));
      }
    }
  }

  function parseAndDisplayTx(to, data) {
    let iface;
    to = to.toLowerCase();
    if (to == VAULT.toLowerCase()) {
      iface = iVault;
    } else if (to == CHECKER.toLowerCase()) {
      iface = iVaultValueChecker;
    } else {
      return div(data);
    }

    const outputEl = div("");

    // Think
    let successParse = false;
    let parsed;
    try {
      parsed = iface.parseTransaction({ data: data });
      successParse = true;
    } catch {}

    if (!successParse) {
      outputEl.appendChild(element("h2", "Invalid Data"));
      return outputEl;
    }

    outputEl.appendChild(DecodeViewEL(parsed));
    return outputEl;
  }

  // Draw a parsed transaction
  function DecodeViewEL(parsed) {
    const outputEl = div("");
    const parens = parsed.args.length == 0 ? "()" : " (...)";
    outputEl.appendChild(element("h2", "➠ " + parsed.name + parens));

    const tableEl = element("table", "");

    for (let i = 0; i < parsed.args.length; i++) {
      const value = parsed.args[i];
      const input = parsed.functionFragment.inputs[i];

      const rowEl = element("tr");
      rowEl.appendChild(element("th", input.name));

      const values = Array.isArray(value) ? value : [value];
      const cells = values.map((v, j) => {
        if (v.toString().startsWith("0x")) {
          // Bad
          return AddressEL(v);
        } else if (v._isBigNumber) {
          return DecimalEL(v, decimalHints(parsed, input, j));
        } else {
          return div(v);
        }
      });
      cells.forEach((x) => rowEl.appendChild(element("td", [x])));
      tableEl.appendChild(rowEl);
    }

    outputEl.appendChild(tableEl);
    return outputEl;
  }

  function parseMultisend(data) {
    const innerTxs = [];
    let type, address, value, innerData;
    while (data.length > 0) {
      [type, data] = nom(data, 1);
      if (type != "0x00") {
        throw "Bad multi send type";
      }
      [address, data] = nom(data, 20);
      [value, data] = nom(data, 32);
      if (
        value !=
        "0x0000000000000000000000000000000000000000000000000000000000000000"
      ) {
        throw "Non zero value";
      }
      [len, data] = nom(data, 32);
      len = ethers.utils.formatUnits(len, 0);
      [innerData, data] = nom(data, len);

      innerTxs.push({ to: address, data: innerData });
    }

    return innerTxs;
  }

  function nom(v, size) {
    return ["0x" + v.slice(0, size * 2), v.slice(size * 2)];
  }

  // Draw an address, checking it against known addresses
  function AddressEL(value) {
    const name = CONTRACT_NAMES[value];
    if (name) {
      return div("✓ " + name, { class: "good pill" });
    } else {
      return div("⛔️ " + value, { class: "bad pill" });
    }
  }

  // Draw a decimal number value
  function DecimalEL(value, decimals) {
    let v = value;
    let leftovers;
    if (decimals == 6) {
      v = v.div(1000000);
      leftovers = value.sub(v.mul(1000000));
    } else if (decimals == 18) {
      v = v.div(1000000).div(1000000).div(1000000);
      leftovers = value.sub(v.mul(1000000).mul(1000000).mul(1000000));
    } else if (decimals == 0) {
      v = v;
    } else {
      return div("⛔️ " + v, { class: "bad pill" });
    }
    contents = [span(parseInt(v).toLocaleString("en-US"), { class: "number" })];
    if (leftovers && leftovers.gt(0)) {
      contents.push(span("."));
      contents.push(
        span(leftovers.toString().padStart(decimals, "0"), {
          class: "decimals",
        })
      );
    }
    contents.push(span(" e" + decimals.toString(), { class: "decimals" }));

    return div(contents, { class: "neutral pill" });
  }

  // How many decimals should we use?
  function decimalHints(parsed, input, i) {
    if (parsed.sighash == "0x7fe2d393") {
      // reallocate amounts use currency decimals
      return DECIMALS[parsed.args[2][i]] || 0;
    }
    if (parsed.sighash == "0x2cd47c23") {
      // reallocate amounts use currency decimals
      return 18;
    }
    return 0; // Default
  }

  // React in 10 lines
  div = (contents, attr) => element("div", contents, attr);
  span = (contents, attr) => element("span", contents, attr);
  function element(name, contents, attr = []) {
    const me = document.createElement(name);
    if (Array.isArray(contents)) {
      for (const el of contents) {
        me.appendChild(el);
      }
    } else {
      me.textContent = contents;
    }
    for (var k in attr) {
      me.setAttribute(k, attr[k]);
    }
    return me;
  }

  return { app };
})();

