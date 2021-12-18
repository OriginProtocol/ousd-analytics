const strategistCreator = (function () {
  const ethers = window.ethers;
  const iVault = new ethers.utils.Interface(abiVault.abi);
  const iVaultValueChecker = new ethers.utils.Interface(
    abiVaultValueChecker.abi
  );

  let fromEl,
    toEl,
    daiEl,
    usdcEl,
    usdtEl,
    maxLossEl,
    outputEl = undefined;

  // Constants
  const CONTRACT_ADDRESSES = {
    "AAVE Strat": "0x5e3646A1Db86993f73E6b74A57D8640B69F7e259",
    "Compound Strat": "0x9c459eeb3FA179a40329b81C1635525e9A0Ef094",
    "Convex Strat": "0xEA2Ef2e2E5A749D4A66b41Db9aD85a38Aa264cb3",
  };

  const MULTI_SEND_ADDRESS = "0x40a2accbd92bca938b02010e17a5b8929b49130d";
  const VAULT = "0xE75D77B1865Ae93c7eaa3040B038D7aA7BC02F70";
  const CHECKER = "0x5B98B3255522E95f842967723Ee4Cc7dCEaa9150";

  // App hooks up to events
  function app(opts) {
    fromEl = opts.fromEl;
    toEl = opts.toEl;
    daiEl = opts.daiEl;
    usdcEl = opts.usdcEl;
    usdtEl = opts.usdtEl;
    maxLossEl = opts.maxLossEl;
    outputEl = opts.outputEl;

    // There are finite, but very large, number of reasons why
    // the following two lines could be a bad idea.
    // But as Galleio allegedly muttered "Eppur si muove"
    Object.keys(opts).forEach(
      (x) =>
        (opts[x].onkeyup = () => {
          refresh();
        })
    );
    Object.keys(opts).forEach(
      (x) =>
        (opts[x].onchange = () => {
          refresh();
        })
    );

    refresh();
  }

  // Redraw the output
  function refresh() {
    outputEl.innerHTML = "";

    const to = CONTRACT_ADDRESSES[toEl.value];
    const from = CONTRACT_ADDRESSES[fromEl.value];
    const daiAmount = daiEl.value;
    const usdcAmount = usdcEl.value;
    const usdtAmount = usdtEl.value;
    const maxLoss = maxLossEl.value;

    let errors = [];
    let amounts = [];
    let currencies = [];

    // Check
    const needsCheck =
      to == CONTRACT_ADDRESSES["Convex Strat"] ||
      from == CONTRACT_ADDRESSES["Convex Strat"];

    // Build reallocate TX
    if (daiAmount) {
      currencies.push("0x6B175474E89094C44Da98b954EedeAC495271d0F");
      amounts.push(parseNumber(daiAmount, 18));
    }
    if (usdcAmount) {
      currencies.push("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48");
      amounts.push(parseNumber(usdcAmount, 6));
    }
    if (usdtAmount) {
      currencies.push("0xdAC17F958D2ee523a2206206994597C13D831ec7");
      amounts.push(parseNumber(usdtAmount, 6));
    }
    const reallocateData = iVault.encodeFunctionData("reallocate", [
      from,
      to,
      currencies,
      amounts,
    ]);

    // Build final data
    let finalData;
    if (needsCheck) {
      try {
        const takeSnapshotData =
          iVaultValueChecker.encodeFunctionData("takeSnapshot");
        const checkLossData = iVaultValueChecker.encodeFunctionData(
          "checkLoss",
          [parseNumber(maxLoss, 18)]
        );
        finalData =
          "0x8d80ff0a" +
          [
            // multisend signature
            packInnerTx(CHECKER, takeSnapshotData),
            packInnerTx(VAULT, reallocateData),
            packInnerTx(CHECKER, checkLossData),
          ]
            .join("")
            .replace(/0x/g, "");
        console.log("========");
        console.log(takeSnapshotData);
        console.log("🚌", reallocateData)
        console.log(checkLossData);
      } catch (e) {
        console.error(e);
      }
    } else {
      finalData = reallocateData;
    }

    // Output to UI

    if (finalData) {
      outputEl.appendChild(element("h3", "Transaction Data"));
      outputEl.appendChild(element("textarea", finalData, {}));
    }

    if (needsCheck) {
      maxLossEl.removeAttribute("disabled");
      maxLossEl.style.opacity = 1;
      if (maxLossEl.value == "n/a") {
        maxLossEl.value = "10";
        setTimeout(refresh, 1);
      }
    } else {
      maxLossEl.setAttribute("disabled", "true");
      maxLossEl.style.opacity = 0.5;
      maxLossEl.value = "n/a";
    }
  }

  function packInnerTx(to, input) {
    actualLength = (input.length - 2) / 2; // From hex string
    return ethers.utils.solidityPack(
      ["uint8", "address", "uint256", "uint256", "bytes"],
      [
        0, // type, always zero
        to, // to address
        0, // eth value, always zerow
        actualLength, // input data length
        input, // Data
      ]
    );
  }

  function buildCheckerVerify(maxLoss) {
    return ethers.utils.solidityPack(
      ["bytes", "int256"],
      [
        "0xaabbccdd", // signature
        parseNumber(maxLoss, 18), // amount
      ]
    );
  }

  function parseNumber(v, decimals) {
    v = v.replace(/,/g, "");
    return ethers.utils.parseUnits(v, decimals);
  }

  // Poor man's React
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
