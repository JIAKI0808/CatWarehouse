(() => {
  const root = document.querySelector(".app");
  const overlay = root.querySelector("[data-overlay]");
  const dialogContent = root.querySelector("[data-dialog-content]");
  const toastBox = root.querySelector("[data-toast-box]");
  let toastTimer;
  let confirmAction = null;
  let selectedChoice = "";

  const fakeItems = {
    "四川红花椒": { price: "18.00", quantity: "2", unit: "袋" },
    "酱油": { price: "12.50", quantity: "1", unit: "瓶" },
    "橄榄油": { price: "56.00", quantity: "3", unit: "瓶" },
  };

  function showToast(message) {
    toastBox.textContent = message;
    toastBox.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastBox.classList.remove("show"), 1800);
  }

  function closeDialog() {
    overlay.classList.remove("open");
    confirmAction = null;
  }

  function openDialog(type, name = "") {
    if (type === "category") {
      dialogContent.innerHTML = '<h2>选择分类</h2><p class="dialog-intro">切换后将显示对应的演示库存。</p><div class="choice-list"><button class="choice active" type="button" data-choice="食品杂货">食品杂货 <span>6 袋</span></button><button class="choice" type="button" data-choice="清洁用品">清洁用品 <span>4 件</span></button><button class="choice" type="button" data-choice="宠物用品">宠物用品 <span>3 件</span></button></div>';
      selectedChoice = "食品杂货";
      confirmAction = () => {
        const title = root.querySelector(".nav-title, .after-title");
        if (title) title.childNodes[0].textContent = `${selectedChoice} `;
        const infoName = root.querySelector(".before-info b");
        if (infoName) infoName.textContent = selectedChoice;
        showToast(`已切换：${selectedChoice}（演示数据）`);
      };
    } else if (type === "more") {
      dialogContent.innerHTML = '<h2>更多操作</h2><p class="dialog-intro">这里只演示操作反馈，不会上传或修改真实数据。</p><div class="choice-list"><button class="choice" type="button" data-choice="上传单据">上传单据 <span>›</span></button><button class="choice" type="button" data-choice="导入数据">导入数据 <span>›</span></button><button class="choice" type="button" data-choice="导出数据">导出数据 <span>›</span></button></div>';
      confirmAction = () => showToast("演示操作已触发");
    } else {
      const item = fakeItems[name] || { price: "", quantity: "", unit: "袋" };
      dialogContent.innerHTML = `<h2>${name ? "编辑物品" : "新增物品"}</h2><p class="dialog-intro">演示表单 · 数据不会保存到产品。</p><div class="form-field"><label>物品名称</label><input data-name value="${name}" placeholder="例如：猫粮" /></div><div class="form-field"><label>价格</label><input value="${item.price}" inputmode="decimal" placeholder="0.00" /></div><div class="form-field"><label>库存数量</label><input value="${item.quantity}" inputmode="numeric" placeholder="0" /></div><div class="form-field"><label>单位</label><input value="${item.unit}" /></div>`;
      confirmAction = () => {
        const itemName = dialogContent.querySelector("[data-name]").value.trim();
        showToast(itemName ? `已模拟保存：${itemName}` : "请输入物品名称");
        return Boolean(itemName);
      };
    }
    overlay.classList.add("open");
    const firstField = dialogContent.querySelector("input");
    if (firstField) setTimeout(() => firstField.focus(), 0);
  }

  root.querySelectorAll("[data-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      root.querySelectorAll("[data-tab]").forEach((item) => item.classList.toggle("active", item === tab));
      root.querySelectorAll("[data-page]").forEach((page) => page.classList.toggle("active", page.dataset.page === tab.dataset.tab));
      const titles = { inventory: "食品杂货", analytics: "数据分析", ledger: "账本", pricing: "售价管理", settings: "设置" };
      const title = root.querySelector(".nav-title, .after-title");
      const isInventory = tab.dataset.tab === "inventory";
      if (title) {
        title.childNodes[0].textContent = `${titles[tab.dataset.tab]} `;
        title.style.pointerEvents = isInventory ? "" : "none";
        const arrow = title.querySelector("span, img");
        if (arrow) arrow.style.display = isInventory ? "" : "none";
      }
      root.querySelectorAll(".nav-left, .nav-right, .after-actions").forEach((actions) => {
        actions.style.visibility = isInventory ? "" : "hidden";
      });
    });
  });

  root.querySelectorAll("[data-dialog]").forEach((button) => button.addEventListener("click", () => openDialog(button.dataset.dialog)));
  root.querySelectorAll("[data-edit]").forEach((item) => item.addEventListener("click", () => openDialog("edit", item.dataset.edit)));
  root.querySelectorAll("[data-toast]").forEach((button) => button.addEventListener("click", () => showToast(button.dataset.toast)));

  root.addEventListener("click", (event) => {
    const choice = event.target.closest("[data-choice]");
    if (!choice) return;
    selectedChoice = choice.dataset.choice;
    dialogContent.querySelectorAll("[data-choice]").forEach((item) => item.classList.toggle("active", item === choice));
  });

  root.querySelector("[data-close]").addEventListener("click", closeDialog);
  root.querySelector("[data-confirm]").addEventListener("click", () => {
    const shouldClose = confirmAction ? confirmAction() : true;
    if (shouldClose !== false) closeDialog();
  });
  overlay.addEventListener("click", (event) => { if (event.target === overlay) closeDialog(); });

  root.querySelectorAll(".toggle").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const isOn = toggle.classList.toggle("on");
      toggle.setAttribute("aria-pressed", String(isOn));
      if (toggle.hasAttribute("data-theme")) document.body.classList.toggle("dark", isOn);
    });
  });

  const search = root.querySelector("[data-search]");
  if (search) {
    search.addEventListener("input", () => {
      const query = search.value.trim().toLowerCase();
      root.querySelectorAll("[data-filter]").forEach((item) => {
        item.hidden = Boolean(query) && !item.dataset.filter.toLowerCase().includes(query);
      });
    });
  }

  const overview = root.querySelector("[data-overview]");
  if (overview) {
    const trigger = overview.querySelector("[data-overview-toggle]");
    const button = trigger.querySelector("button");
    const icon = trigger.querySelector("img");
    trigger.addEventListener("click", () => {
      const expanded = overview.classList.toggle("collapsed") === false;
      button.setAttribute("aria-expanded", String(expanded));
      button.setAttribute("aria-label", expanded ? "收起库存概况" : "展开库存概况");
      icon.src = expanded ? "../assets/icon-arrow-down-2.svg" : "../assets/icon-arrow-right-2.svg";
    });
  }
})();
