/**
 * 简体中文语言包（默认语言）。
 *
 * ## 两个分区，两种来源
 *
 * - `app.*` —— **界面文案**，由本文件（也就是前端）拥有。
 *   必须在后端尚未应答时就能渲染：离线 / 连不上服务端是本应用的**正常状态**
 *   （设置页专门有「测试连接」就是这个原因）。做成远程依赖等于给首屏加一个失败点。
 * - `backend.*` —— **后端自己产生的文案**的对照表，键就是后端返回的 `detail` 原文。
 *   后端目录在 `CwServer/locales/zh-CN.json`，**两边必须保持一致**。
 *   用 `translateBackendMessage()` 查询，查不到就原样显示，绝不显示空串。
 *
 * ## 为什么导出 `MessageSchema`
 *
 * `MessageSchema` 由本文件推导，`en-US.ts` 用它约束自己 ——
 * **漏翻一个键会在 `vue-tsc` 阶段直接报错**，而不是等到界面上显示出一串 key。
 */

const zhCN = {
  app: {
    nav: {
      inventory: '库存',
      analytics: '数据分析',
      ledger: '账本',
      pricing: '售价管理',
      settings: '设置',
    },
    settingsPage: {
      language: '语言',
      languageNote: '切换后立即生效；服务器不可达时只保存在本机',
      languageSyncFailed: '已在本机切换，但未能同步到服务器',
    },

    // 「公共词汇」—— 全站反复出现的名词/按钮/提示。先抽到这里再逐文件替换，
    // 否则同一个「保存」会在 10 个文件里各写一份，改一处漏九处。
    // 只在**字面确实相同**时才复用；语境不同就各自开一个 key（见 inventory.*）。
    common: {
      name: '名称',
      description: '描述',
      price: '价格',
      stock: '库存',
      updatedAt: '更新日期',
      expiresAt: '过期时间',
      expired: '已过期',
      recorder: '录入人',
      actions: '操作',
      edit: '编辑',
      remove: '删除',
      save: '保存',
      cancel: '取消',
      close: '关闭',
      create: '新增',
      confirm: '确定',
      yes: '是',
      no: '否',
      unit: '单位',
      notes: '备注',
      icon: '图标',
      iconColor: '图标颜色',
      category: '分类',
      subCategory: '子分类',
      noData: '暂无数据',
      noDescription: '暂无描述',
      // 「确认删除」原先放在 inventory 下，但账本、售价都要用同一句 —— 提到 common。
      // （提出来的时机是它出现**第三个**使用者的那一刻，不是第一个。）
      confirmDeleteTitle: '确认删除',
      quantity: '库存数量',
      inputName: '请输入名称',
      inputDescription: '请输入描述',
      inputNotes: '请输入备注',
      inputUnit: '请输入单位',
      inputRecorder: '请输入录入人',
      selectExpiry: '请选择过期时间',
    },

    inventory: {
      title: '库存列表',
      emptyHint: '等待录入好东西',
      viewTable: '表格',
      viewCard: '卡片',
      uploadReceipt: '上传单据',
      exportData: '导出数据',
      importData: '导入数据',
      exportSuccess: '导出成功',
      exportFailed: '导出失败',
      uploadSuccess: '上传成功',
      uploadFailed: '上传失败',
      confirmDeleteCategory: '确定要删除大类「{name}」吗？',
      confirmDeleteSubCategory: '确定要删除子分类「{name}」吗？',
      addCategory: '新增大类',
      editCategory: '编辑大类',
      addSubCategory: '新增子分类',
      editSubCategory: '编辑子分类',
      addItem: '新增物品',
      editItem: '编辑物品',
    },

    ledger: {
      title: '账本',
      scopeDay: '按天',
      scopeWeek: '按周',
      scopeMonth: '按月',
      scopeYear: '按年',
      typeAll: '全部',
      typeIncome: '收入',
      typeExpense: '支出',
      amount: '金额',
      type: '类型',
      date: '日期',
      platform: '平台',
      person: '记账人',
      budgetOverview: '预算概览',
      chartTitle: '收支统计',
      chartAmountAxis: '金额 (¥)',
      searchPlaceholder: '搜索描述/平台/记账人',
      create: '新增',
      addBill: '新增账单',
      editBill: '编辑账单',
      deleteConfirm: '确定要删除这条账单吗？',
      // 年月与星期是**语言相关的格式**，不是可以逐字替换的文案：
      // 英文是 "2026" / "Jan" / "Su"，照搬「年」「月」会出洋相。所以它们也进语言包。
      yearLabel: '{year}年',
      months: [
        '1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月',
      ],
      weekdays: ['日', '一', '二', '三', '四', '五', '六'],
      inputPlatform: '支付宝/微信/银行等',
      inputDescription: '消费描述',
      inputPerson: '谁记的',
    },

    analytics: {
      title: '数据分析',
      totalItems: '总库存数',
      totalValue: '总库存价值',
      totalIncome: '总收入',
      totalExpense: '总支出',
      selectCategory: '选择大类',
      selectSubCategory: '选择子类',
      emptyTrend: '请选择大类和子类查看趋势',
      // 图表的「指标名」与「坐标轴名」分开：坐标轴带单位，指标名不带。
      // 混成一个 key 会让饼图的扇区名叫成「数量 (斤)」，很怪。
      metric: {
        quantity: '数量',
        price: '价格',
        totalPrice: '总价',
        unitPrice: '单价',
        stock: '库存',
      },
      axis: {
        quantity: '数量 ({unit})',
        price: '价格 (¥)',
        totalPrice: '总价 (¥)',
        unitPrice: '单价 (¥)',
        amount: '金额 (¥)',
      },
      chart: {
        quantityTrend: '数量趋势',
        priceTrend: '价格趋势',
        totalPriceTrend: '总价趋势',
        unitPriceTrend: '单价趋势',
        quantityDistribution: '数量分布',
        priceComparison: '价格对比',
        categoryStockShare: '分类库存占比',
        monthlyCompare: '月度收支对比',
      },
    },

    // 售价区。这里的「分类 / 子分类」是 **PricingCategory / PricingSubCategory**，
    // 与库存区的大类/子分类是**不同的领域对象** —— 所以即便中文逐字相同也各开各的 key，
    // 改售价页的措辞不会连带改掉库存页。
    pricing: {
      title: '售价管理',
      productName: '商品名',
      cost: '成本',
      suggestedPrice: '建议售价',
      discount: '折扣系数',
      recordDate: '记录日期',
      searchPlaceholder: '搜索商品名',
      addPricing: '新增售价',
      editPricing: '编辑售价',
      deleteConfirm: '确定要删除这条售价记录吗？',
      categoryTitle: '售价分类',
      addCategory: '新增分类',
      editCategory: '编辑分类',
      categoryNamePlaceholder: '分类名称',
      addSubCategory: '新增子分类',
      editSubCategory: '编辑子分类',
      subCategoryNamePlaceholder: '子分类名称',
      inputName: '请输入商品名',
    },

    // 录入区（导入 / 上传）。上传弹窗的标题直接复用 `inventory.uploadReceipt` ——
    // 菜单项「上传单据」打开的就是这个弹窗，是**同一个东西**。
    intake: {
      importTitle: '导入数据',
      importDropHint: '点击或者拖动 JSON 文件到此区域',
      importConflicts: '发现以下冲突项，勾选的项目将被跳过：',
      importSkipColumn: '跳过',
      importTypeColumn: '类型',
      importNameColumn: '名称',
      importKindCategory: '大类',
      importKindSubCategory: '子分类',
      importDoneTitle: '导入完成',
      importDoneDesc: '新增大类 {categories} 个，子分类 {subCategories} 个，物品 {items} 个',
      importConfirm: '确认导入',
      parseFailed: '文件解析失败',
      importFailed: '导入失败',
      uploadDropHint: '点击或者拖动图片到此区域上传',
      upload: '上传',
    },

    notify: {
      stockAlerts: '库存预警',
      lowStock: '低库存',
      systemNotifications: '系统通知',
      markRead: '已读',
      empty: '暂无通知',
    },

    // 图标选择器的 48 个 tooltip。键就是 @vicons/ionicons5 的组件名 ——
    // 换图标库时键跟着变，比「按序号 icon1..icon48」可维护得多。
    icons: {
      FolderOutline: '文件夹',
      CartOutline: '购物车',
      ShirtOutline: '衣物',
      HardwareChipOutline: '芯片',
      NutritionOutline: '营养',
      CameraOutline: '相机',
      GameControllerOutline: '游戏',
      BookOutline: '书本',
      MusicalNotesOutline: '音乐',
      FitnessOutline: '健身',
      HeartOutline: '心形',
      StarOutline: '星形',
      FlashlightOutline: '手电',
      ColorPaletteOutline: '调色板',
      CubeOutline: '立方体',
      DiamondOutline: '钻石',
      HomeOutline: '家居',
      CarOutline: '汽车',
      WalkOutline: '步行',
      AirplaneOutline: '飞机',
      BoatOutline: '船',
      PawOutline: '宠物',
      LeafOutline: '植物',
      FlameOutline: '火焰',
      WaterOutline: '水滴',
      SunnyOutline: '太阳',
      MoonOutline: '月亮',
      CloudyOutline: '云朵',
      UmbrellaOutline: '雨伞',
      GiftOutline: '礼物',
      SparklesOutline: '闪光',
      TrophyOutline: '奖杯',
      WineOutline: '酒杯',
      CafeOutline: '咖啡',
      PizzaOutline: '披萨',
      MedicalOutline: '医疗',
      WalletOutline: '钱包',
      KeyOutline: '钥匙',
      LockClosedOutline: '锁',
      GlobeOutline: '地球',
      MapOutline: '地图',
      TimeOutline: '时间',
      BeerOutline: '啤酒',
      BugOutline: '昆虫',
      FishOutline: '鱼',
      BulbOutline: '灯泡',
      ExtensionPuzzleOutline: '拼图',
      RibbonOutline: '丝带',
    },
  },
  backend: {
    'Category not found': '分类不存在',
    'SubCategory not found': '子分类不存在',
    'Item not found': '物品不存在',
    'Tag not found': '标签不存在',
    'Notification not found': '通知不存在',
    'Budget not found': '预算不存在',
    'Ledger item not found': '账目不存在',
    'Recurring bill not found': '定时账单不存在',
    'Pricing not found': '售价记录不存在',
    'Pricing category not found': '售价分类不存在',
    'Pricing sub-category not found': '售价子分类不存在',
    'empty file': '上传的文件为空',
    '科学的管理每一颗螺丝钉': '科学的管理每一颗螺丝钉',
  },
}

export type MessageSchema = typeof zhCN
export default zhCN
