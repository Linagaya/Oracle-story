"""
甲骨文知识库 - 用于难以定义字符的大致意思揣摩

包含:
1. 常见部首/形符及其含义
2. 象形字特征库
3. 卜辞常用语境
4. 污染/残缺字判断规则
5. 形近字分组
"""

# ==================== 常见甲骨文部首/形符及其含义 ====================
ORACLE_RADICALS = {
    # 人体相关
    "人": {"meaning": "人、人类", "category": "人体", "features": ["侧面人形", "站立姿态"]},
    "女": {"meaning": "女性、妇女", "category": "人体", "features": ["跪坐姿态", "双手交叉"]},
    "子": {"meaning": "孩子、子嗣", "category": "人体", "features": ["婴儿形态", "头部较大"]},
    "口": {"meaning": "口、嘴巴、说话", "category": "人体", "features": ["方形或圆形", "开口状"]},
    "目": {"meaning": "眼睛、看", "category": "人体", "features": ["眼睛形状", "眼眶+瞳孔"]},
    "耳": {"meaning": "耳朵、听", "category": "人体", "features": ["耳朵形状"]},
    "手": {"meaning": "手、抓取", "category": "人体", "features": ["手掌+手指"]},
    "足": {"meaning": "脚、行走", "category": "人体", "features": ["脚形"]},
    "心": {"meaning": "心脏、心思", "category": "人体", "features": ["心脏形状"]},
    "首": {"meaning": "头、首领", "category": "人体", "features": ["头部侧面", "有发"]},
    
    # 自然相关
    "日": {"meaning": "太阳、日子、白天", "category": "自然", "features": ["圆形", "中间有一点"]},
    "月": {"meaning": "月亮、月份、夜晚", "category": "自然", "features": ["弯月形"]},
    "山": {"meaning": "山、山峰", "category": "自然", "features": ["三座山峰"]},
    "水": {"meaning": "水、河流、流动", "category": "自然", "features": ["水波纹", "弯曲流线"]},
    "火": {"meaning": "火、火焰、燃烧", "category": "自然", "features": ["火焰向上", "烟焰形"]},
    "雨": {"meaning": "雨、下雨", "category": "自然", "features": ["天空+雨滴"]},
    "云": {"meaning": "云、云彩", "category": "自然", "features": ["云气回转形"]},
    "土": {"meaning": "土、土地、社神", "category": "自然", "features": ["土堆形", "地上有块"]},
    "石": {"meaning": "石头、岩石", "category": "自然", "features": ["石块形"]},
    "田": {"meaning": "田、田地、耕种", "category": "自然", "features": ["方块分割", "井田形"]},
    "川": {"meaning": "河流、川流", "category": "自然", "features": ["三笔曲线", "水流"]},
    
    # 动物相关
    "牛": {"meaning": "牛、牲畜", "category": "动物", "features": ["牛头正面", "两角向上"]},
    "羊": {"meaning": "羊、牲畜", "category": "动物", "features": ["羊头正面", "两角下弯"]},
    "马": {"meaning": "马", "category": "动物", "features": ["马侧面", "鬃毛+四足+尾"]},
    "豕": {"meaning": "猪", "category": "动物", "features": ["猪形", "肥腹+尾下垂"]},
    "犬": {"meaning": "狗", "category": "动物", "features": ["狗侧面", "瘦腹+尾上翘"]},
    "鹿": {"meaning": "鹿", "category": "动物", "features": ["鹿角分叉"]},
    "虎": {"meaning": "虎", "category": "动物", "features": ["虎口大张", "有斑纹"]},
    "鸟": {"meaning": "鸟、飞禽", "category": "动物", "features": ["鸟侧面", "有翅有尾"]},
    "隹": {"meaning": "短尾鸟", "category": "动物", "features": ["鸟形", "短尾"]},
    "鱼": {"meaning": "鱼", "category": "动物", "features": ["鱼形", "有鳞有尾"]},
    "龟": {"meaning": "龟", "category": "动物", "features": ["龟形", "有甲"]},
    "龙": {"meaning": "龙", "category": "动物", "features": ["龙形", "有角有鳞"]},
    "羽": {"meaning": "羽毛、翅膀", "category": "动物", "features": ["羽毛形"]},
    "角": {"meaning": "角、兽角", "category": "动物", "features": ["角形"]},
    
    # 植物相关
    "木": {"meaning": "木、树木", "category": "植物", "features": ["树形", "干+枝+根"]},
    "禾": {"meaning": "禾、谷物、庄稼", "category": "植物", "features": ["禾穗下垂"]},
    "黍": {"meaning": "黍、黄米", "category": "植物", "features": ["禾+散穗"]},
    "来": {"meaning": "麦、小麦", "category": "植物", "features": ["麦芒向上"]},
    "桑": {"meaning": "桑树", "category": "植物", "features": ["桑树多枝叶"]},
    "竹": {"meaning": "竹子", "category": "植物", "features": ["竹叶下垂"]},
    "果": {"meaning": "果实、果子", "category": "植物", "features": ["树上结果"]},
    
    # 建筑/器物
    "宀": {"meaning": "房屋、家宅", "category": "建筑", "features": ["房屋顶", "覆盖形"]},
    "门": {"meaning": "门、门户", "category": "建筑", "features": ["两扇门"]},
    "户": {"meaning": "单扇门", "category": "建筑", "features": ["单扇门形"]},
    "邑": {"meaning": "城邑、聚落", "category": "建筑", "features": ["囗+跪坐人"]},
    "京": {"meaning": "高台、京城", "category": "建筑", "features": ["高建筑形"]},
    "高": {"meaning": "高、高台", "category": "建筑", "features": ["高台上有建筑"]},
    "井": {"meaning": "井", "category": "建筑", "features": ["井栏方形"]},
    "仓": {"meaning": "粮仓、仓库", "category": "建筑", "features": ["仓房形"]},
    "鼎": {"meaning": "鼎、礼器", "category": "器物", "features": ["鼎形", "三足两耳"]},
    "酉": {"meaning": "酒尊、酒", "category": "器物", "features": ["酒尊形"]},
    "爵": {"meaning": "爵、酒器", "category": "器物", "features": ["爵形", "有流有尾"]},
    "皿": {"meaning": "器皿", "category": "器物", "features": ["器皿形"]},
    "戈": {"meaning": "戈、兵器", "category": "器物", "features": ["戈形", "长柄+横刃"]},
    "弓": {"meaning": "弓", "category": "器物", "features": ["弓形"]},
    "矢": {"meaning": "箭", "category": "器物", "features": ["箭形", "镞+杆+羽"]},
    "刀": {"meaning": "刀", "category": "器物", "features": ["刀形"]},
    "斤": {"meaning": "斧、斤", "category": "器物", "features": ["斧形"]},
    "车": {"meaning": "车", "category": "器物", "features": ["车形", "轮+轴+辕"]},
    "舟": {"meaning": "船、舟", "category": "器物", "features": ["船形"]},
    "网": {"meaning": "网", "category": "器物", "features": ["网形"]},
    "贝": {"meaning": "贝壳、货币", "category": "器物", "features": ["贝壳形"]},
    "玉": {"meaning": "玉、玉器", "category": "器物", "features": ["玉串形"]},
    "册": {"meaning": "简册、典籍", "category": "器物", "features": ["竹简编连"]},
    "卜": {"meaning": "占卜、卜兆", "category": "器物", "features": ["卜兆裂纹"]},
    "示": {"meaning": "神主、祭祀", "category": "器物", "features": ["神主牌位"]},
    
    # 数字/方位
    "一": {"meaning": "数字一", "category": "数字", "features": ["一横"]},
    "二": {"meaning": "数字二", "category": "数字", "features": ["二横"]},
    "三": {"meaning": "数字三", "category": "数字", "features": ["三横"]},
    "四": {"meaning": "数字四", "category": "数字", "features": ["四横或方形"]},
    "五": {"meaning": "数字五", "category": "数字", "features": ["X形"]},
    "六": {"meaning": "数字六", "category": "数字", "features": ["入形"]},
    "七": {"meaning": "数字七", "category": "数字", "features": ["十字形"]},
    "八": {"meaning": "数字八", "category": "数字", "features": ["两笔相背"]},
    "九": {"meaning": "数字九", "category": "数字", "features": ["弯曲形"]},
    "十": {"meaning": "数字十", "category": "数字", "features": ["竖画"]},
    "上": {"meaning": "上、上方", "category": "方位", "features": ["长横+短横在上"]},
    "下": {"meaning": "下、下方", "category": "方位", "features": ["长横+短横在下"]},
    "中": {"meaning": "中间、中央", "category": "方位", "features": ["旗帜形", "中竖"]},
    "东": {"meaning": "东、东方", "category": "方位", "features": ["日在木中"]},
    "西": {"meaning": "西、西方", "category": "方位", "features": ["鸟巢形"]},
    "南": {"meaning": "南、南方", "category": "方位", "features": ["乐器形"]},
    "北": {"meaning": "北、北方", "category": "方位", "features": ["两人相背"]},
    
    # 祭祀/鬼神
    "且": {"meaning": "祖、祖先", "category": "祭祀", "features": ["神主牌位"]},
    "鬼": {"meaning": "鬼、鬼神", "category": "祭祀", "features": ["人+大头"]},
    "帝": {"meaning": "上帝、天帝", "category": "祭祀", "features": ["花蒂形/神形"]},
    "王": {"meaning": "王", "category": "祭祀", "features": ["斧钺形", "三横一竖"]},
    "巫": {"meaning": "巫、巫师", "category": "祭祀", "features": ["两工交叉"]},
    "祝": {"meaning": "祝、祷告", "category": "祭祀", "features": ["人跪+示+口"]},
    "祭": {"meaning": "祭、祭祀", "category": "祭祀", "features": ["手持肉+示"]},
    
    # 干支
    "甲": {"meaning": "甲、天干", "category": "干支", "features": ["十字形+框"]},
    "乙": {"meaning": "乙、天干", "category": "干支", "features": ["弯曲形"]},
    "丙": {"meaning": "丙、天干", "category": "干支", "features": ["鱼尾形"]},
    "丁": {"meaning": "丁、天干", "category": "干支", "features": ["钉子形"]},
    "戊": {"meaning": "戊、天干", "category": "干支", "features": ["兵器形"]},
    "己": {"meaning": "己、天干", "category": "干支", "features": ["绳索形"]},
    "庚": {"meaning": "庚、天干", "category": "干支", "features": ["兵器形"]},
    "辛": {"meaning": "辛、天干", "category": "干支", "features": ["刑具形"]},
    "壬": {"meaning": "壬、天干", "category": "干支", "features": ["工字变形"]},
    "癸": {"meaning": "癸、天干", "category": "干支", "features": ["交叉形"]},
    "丑": {"meaning": "丑、地支", "category": "干支", "features": ["手形"]},
    "寅": {"meaning": "寅、地支", "category": "干支", "features": ["矢形"]},
    "卯": {"meaning": "卯、地支", "category": "干支", "features": ["两户对开"]},
    "辰": {"meaning": "辰、地支", "category": "干支", "features": ["蚌镰形"]},
    "巳": {"meaning": "巳、地支", "category": "干支", "features": ["子形"]},
    "午": {"meaning": "午、地支", "category": "干支", "features": ["杵形"]},
    "未": {"meaning": "未、地支", "category": "干支", "features": ["木重枝叶"]},
    "申": {"meaning": "申、地支", "category": "干支", "features": ["闪电形"]},
    "戌": {"meaning": "戌、地支", "category": "干支", "features": ["兵器形"]},
    "亥": {"meaning": "亥、地支", "category": "干支", "features": ["豕形"]},
    
    # 卜辞常用
    "贞": {"meaning": "贞问", "category": "卜辞", "features": ["鼎+卜"]},
    "占": {"meaning": "占卜", "category": "卜辞", "features": ["卜+口"]},
    "吉": {"meaning": "吉利", "category": "卜辞", "features": ["士+口"]},
    "祸": {"meaning": "灾祸", "category": "卜辞", "features": ["囗+卜骨"]},
    "岁": {"meaning": "岁、年", "category": "时间", "features": ["斧钺形"]},
    "年": {"meaning": "年、收成", "category": "时间", "features": ["人负禾"]},
    "夕": {"meaning": "夕、夜晚", "category": "时间", "features": ["月亮形无点"]},
    "旬": {"meaning": "旬、十日", "category": "时间", "features": ["十循环"]},
    "今": {"meaning": "今、现在", "category": "时间", "features": ["口+横"]},
    "昔": {"meaning": "昔、过去", "category": "时间", "features": ["日+洪水"]},
    "旦": {"meaning": "旦、早晨", "category": "时间", "features": ["日+地平线"]},
    "大": {"meaning": "大", "category": "其他", "features": ["人正面张臂"]},
    "小": {"meaning": "小", "category": "其他", "features": ["三小点"]},
    "天": {"meaning": "天、天空", "category": "其他", "features": ["大+头顶"]},
    "文": {"meaning": "文、花纹", "category": "其他", "features": ["人+胸前花纹"]},
    "母": {"meaning": "母、母亲", "category": "其他", "features": ["女+两点(乳)"]},
    "父": {"meaning": "父", "category": "其他", "features": ["手+杖/斧"]},
    "臣": {"meaning": "臣、奴隶", "category": "其他", "features": ["竖目形"]},
    "止": {"meaning": "止、脚、停止", "category": "其他", "features": ["脚印形"]},
    "又": {"meaning": "又、有、右", "category": "其他", "features": ["右手形"]},
    "亡": {"meaning": "无、没有", "category": "其他", "features": ["刀+锋芒"]},
    "弗": {"meaning": "不、否定", "category": "其他", "features": ["绳索捆束"]},
    "不": {"meaning": "不、否定", "category": "其他", "features": ["花蒂形"]},
    "毋": {"meaning": "毋、不要", "category": "其他", "features": ["女+两点"]},
    "勿": {"meaning": "勿、不要", "category": "其他", "features": ["刀+血滴"]},
    "其": {"meaning": "其、语气词", "category": "其他", "features": ["簸箕形"]},
    "自": {"meaning": "自、从", "category": "其他", "features": ["鼻子形"]},
    "白": {"meaning": "白、白色", "category": "其他", "features": ["拇指/白米"]},
    "黄": {"meaning": "黄、黄色", "category": "其他", "features": ["人+佩玉"]},
    "明": {"meaning": "明、明亮", "category": "其他", "features": ["日+月"]},
}

# ==================== 形近字分组 ====================
SIMILAR_CHARS = {
    "日": ["曰", "口", "白", "田", "目"],
    "月": ["夕", "肉", "耳"],
    "口": ["日", "曰", "甘", "白", "石"],
    "目": ["日", "臣", "耳"],
    "耳": ["目", "月", "臣"],
    "人": ["入", "八", "卜", "儿"],
    "大": ["天", "夫", "太", "文", "立", "亦"],
    "女": ["母", "每", "毋"],
    "子": ["巳", "了", "孑"],
    "手": ["又", "寸", "爪", "支", "攴"],
    "止": ["之", "出", "足", "疋", "正"],
    "木": ["禾", "来", "麦", "未", "末", "本", "朱"],
    "水": ["川", "泉", "永", "派"],
    "火": ["山", "赤"],
    "山": ["火", "丘", "阜"],
    "牛": ["羊", "牡", "牝"],
    "羊": ["牛", "羌", "美"],
    "马": ["鹿", "犬", "豕", "虎"],
    "犬": ["豕", "马", "狼"],
    "豕": ["犬", "彘", "豚"],
    "鹿": ["马", "麋"],
    "鸟": ["隹", "乌", "燕", "凤"],
    "隹": ["鸟", "雀", "雁", "鸡"],
    "鱼": ["龟", "贝"],
    "贝": ["鼎", "玉", "朋"],
    "王": ["玉", "士", "工", "壬"],
    "玉": ["王", "珏", "班"],
    "田": ["日", "周", "甫", "囿"],
    "戈": ["戊", "戌", "戍", "戎", "我"],
    "弓": ["弔", "夷", "弟"],
    "矢": ["箭", "至", "晋", "侯"],
    "刀": ["刃", "力", "匕", "勿", "利"],
    "车": ["舆", "轮", "轴"],
    "舟": ["船", "凡", "盘"],
    "鼎": ["贝", "鬲", "甗"],
    "酉": ["酒", "奠", "尊", "爵"],
    "宀": ["广", "厂", "户", "门"],
    "门": ["户", "闭", "开", "关"],
    "示": ["主", "宗", "祖", "社", "神"],
    "卜": ["兆", "贞", "占", "外"],
    "册": ["典", "删", "扁"],
    "雨": ["云", "雷", "电", "雪", "雹"],
    "禾": ["木", "黍", "稷", "稻", "麦", "来"],
    "甲": ["七", "十", "田", "申", "由"],
    "乙": ["己", "已", "巳"],
    "丁": ["个", "钉", "口"],
    "戊": ["戌", "戍", "成", "咸"],
    "己": ["已", "巳", "乙", "弓"],
    "庚": ["康", "唐", "庸"],
    "辛": ["妾", "童", "龙", "言"],
    "壬": ["王", "工", "士", "任"],
    "癸": ["癶", "祭", "登"],
    "子": ["巳", "字", "存", "孝"],
    "辰": ["晨", "振", "蜃"],
    "巳": ["子", "已", "己", "祀"],
    "午": ["杵", "许", "马"],
    "未": ["味", "妹", "昧", "木"],
    "申": ["电", "神", "伸", "甲"],
    "酉": ["酒", "犹", "就", "尊"],
    "戌": ["戍", "戊", "成", "威"],
    "亥": ["核", "刻", "豕", "该"],
}

# ==================== 卜辞常见语境模板 ====================
DIVINATION_CONTEXTS = {
    "天气": ["雨", "风", "雷", "电", "霁", "晴", "虹", "云", "雪", "雹"],
    "祭祀": ["祭", "祀", "酒", "牲", "牢", "告", "册", "御", "祖", "妣", "父", "母", "兄", "弟", "示", "帝", "社", "神", "鼎", "酉", "爵"],
    "田猎": ["田", "狩", "逐", "射", "获", "擒", "焚", "驭", "雉", "兔", "鹿", "麋", "豕", "狐", "狼", "虎", "鱼", "犬", "马", "弓", "矢"],
    "征伐": ["征", "伐", "攻", "获", "执", "俘", "戍", "卫", "旅", "师", "族", "羌", "戈", "弓", "矢", "车"],
    "农业": ["禾", "黍", "稷", "麦", "来", "年", "岁", "收", "获", "田", "农", "仓", "廪", "米"],
    "天象": ["日", "月", "星", "云", "雨", "风", "雷", "电", "虹", "霁", "旦", "朝", "暮", "昏", "夕", "明"],
    "灾祸": ["祸", "祟", "咎", "灾", "尤", "凶", "艰", "亡", "丧", "死", "疾", "病"],
    "吉凶": ["吉", "大吉", "弘吉", "引吉", "亡祸", "亡尤", "亡灾", "利", "若"],
    "时间": ["日", "月", "岁", "年", "祀", "旬", "今", "昔", "翌", "来", "春", "秋", "旦", "朝", "暮", "昏", "夕"],
    "数字": ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "百", "千", "万", "朋"],
    "方位": ["东", "西", "南", "北", "中", "上", "下", "左", "右", "内", "外", "前", "后"],
    "人物": ["王", "妇", "子", "侯", "伯", "尹", "臣", "宰", "工", "史", "卜", "巫", "羌", "众", "人"],
    "贡纳": ["入", "来", "氏", "致", "贡", "献", "见", "易", "赐", "赏", "贝", "朋", "玉", "马", "牛", "羊", "豕"],
    "建筑": ["邑", "郭", "京", "高", "门", "户", "宫", "室", "宗", "庙", "家", "宅", "牢", "井", "仓", "廪"],
    "出行": ["行", "步", "走", "出", "入", "往", "来", "去", "逐", "追", "还", "归", "复", "涉", "舟", "车", "马"],
}

# ==================== 污染/残缺字判断特征 ====================
POLLUTION_FEATURES = {
    "严重污染": {
        "description": "图像存在严重污染、模糊或断裂",
        "indicators": ["大面积墨点", "笔画断裂", "拓片不清晰", "有遮挡物"],
        "confidence_range": (0, 0.2),
    },
    "中度污染": {
        "description": "部分笔画受污染或残缺",
        "indicators": ["部分笔画缺失", "有少量污点", "边缘不清晰", "局部磨损"],
        "confidence_range": (0.2, 0.35),
    },
    "轻度污染": {
        "description": "轻微污损，主要笔画可辨",
        "indicators": ["少量污点", "笔画边缘略模糊", "整体字形可辨"],
        "confidence_range": (0.35, 0.5),
    },
    "难以定义": {
        "description": "字形特殊，既非污染也非常见字，可能是异体字、合文或未释读字",
        "indicators": ["字形结构特殊", "笔画组合罕见", "与所有已知字相似度均低", "可能是合文", "可能是专有名", "可能是异体字"],
        "confidence_range": (0.2, 0.5),
    },
}

# ==================== 合文识别 ====================
HEWEN_PATTERNS = {
    "十五": {"components": ["十", "五"], "meaning": "十五"},
    "二十": {"components": ["二", "十"], "meaning": "二十/廿"},
    "三十": {"components": ["三", "十"], "meaning": "三十/卅"},
    "四十": {"components": ["四", "十"], "meaning": "四十/卌"},
    "五十": {"components": ["五", "十"], "meaning": "五十"},
    "六十": {"components": ["六", "十"], "meaning": "六十"},
    "七十": {"components": ["七", "十"], "meaning": "七十"},
    "八十": {"components": ["八", "十"], "meaning": "八十"},
    "九十": {"components": ["九", "十"], "meaning": "九十"},
    "三百": {"components": ["三", "百"], "meaning": "三百"},
    "五百": {"components": ["五", "百"], "meaning": "五百"},
    "二千": {"components": ["二", "千"], "meaning": "二千"},
    "五千": {"components": ["五", "千"], "meaning": "五千"},
    "二朋": {"components": ["二", "朋"], "meaning": "二朋（贝币单位）"},
    "十朋": {"components": ["十", "朋"], "meaning": "十朋（贝币单位）"},
    "亡尤": {"components": ["亡", "尤"], "meaning": "亡尤（无灾）"},
    "亡祸": {"components": ["亡", "祸"], "meaning": "亡祸（无祸）"},
    "亡灾": {"components": ["亡", "灾"], "meaning": "亡灾（无灾）"},
    "亡雨": {"components": ["亡", "雨"], "meaning": "亡雨（不下雨）"},
    "其雨": {"components": ["其", "雨"], "meaning": "其雨（会下雨）"},
    "不雨": {"components": ["不", "雨"], "meaning": "不雨（不下雨）"},
    "大雨": {"components": ["大", "雨"], "meaning": "大雨"},
    "小雨": {"components": ["小", "雨"], "meaning": "小雨"},
    "弘吉": {"components": ["弘", "吉"], "meaning": "弘吉（大吉）"},
    "大吉": {"components": ["大", "吉"], "meaning": "大吉"},
    "引吉": {"components": ["引", "吉"], "meaning": "引吉（长吉）"},
    "小臣": {"components": ["小", "臣"], "meaning": "小臣（官职）"},
    "小子": {"components": ["小", "子"], "meaning": "小子（官职/称谓）"},
    "小王": {"components": ["小", "王"], "meaning": "小王（孝己）"},
    "上帝": {"components": ["上", "帝"], "meaning": "上帝/天帝"},
    "下上": {"components": ["下", "上"], "meaning": "下上/上下神祇"},
    "一月": {"components": ["一", "月"], "meaning": "一月/正月"},
    "二月": {"components": ["二", "月"], "meaning": "二月"},
    "三月": {"components": ["三", "月"], "meaning": "三月"},
    "四月": {"components": ["四", "月"], "meaning": "四月"},
    "五月": {"components": ["五", "月"], "meaning": "五月"},
    "六月": {"components": ["六", "月"], "meaning": "六月"},
    "七月": {"components": ["七", "月"], "meaning": "七月"},
    "八月": {"components": ["八", "月"], "meaning": "八月"},
    "九月": {"components": ["九", "月"], "meaning": "九月"},
    "十月": {"components": ["十", "月"], "meaning": "十月"},
    "十一月": {"components": ["十", "一", "月"], "meaning": "十一月"},
    "十二月": {"components": ["十", "二", "月"], "meaning": "十二月/腊月"},
    "十三月": {"components": ["十", "三", "月"], "meaning": "十三月（闰月）"},
    "大乙": {"components": ["大", "乙"], "meaning": "大乙（成汤）"},
    "大甲": {"components": ["大", "甲"], "meaning": "大甲（先王）"},
    "大庚": {"components": ["大", "庚"], "meaning": "大庚（先王）"},
    "大戊": {"components": ["大", "戊"], "meaning": "大戊（先王）"},
    "中丁": {"components": ["中", "丁"], "meaning": "中丁（先王）"},
    "祖乙": {"components": ["祖", "乙"], "meaning": "祖乙（先王）"},
    "祖辛": {"components": ["祖", "辛"], "meaning": "祖辛（先王）"},
    "祖丁": {"components": ["祖", "丁"], "meaning": "祖丁（先王）"},
    "祖庚": {"components": ["祖", "庚"], "meaning": "祖庚（先王）"},
    "祖甲": {"components": ["祖", "甲"], "meaning": "祖甲（先王）"},
    "父丁": {"components": ["父", "丁"], "meaning": "父丁（先父）"},
    "父甲": {"components": ["父", "甲"], "meaning": "父甲（父辈先王）"},
    "父庚": {"components": ["父", "庚"], "meaning": "父庚（父辈先王）"},
    "父辛": {"components": ["父", "辛"], "meaning": "父辛（父辈先王）"},
    "父乙": {"components": ["父", "乙"], "meaning": "父乙（父辈）"},
    "母庚": {"components": ["母", "庚"], "meaning": "母庚（先妣）"},
    "母辛": {"components": ["母", "辛"], "meaning": "母辛（先妣）"},
    "母壬": {"components": ["母", "壬"], "meaning": "母壬（先妣）"},
    "武丁": {"components": ["武", "丁"], "meaning": "武丁（商王）"},
    "帝乙": {"components": ["帝", "乙"], "meaning": "帝乙（商王）"},
    "帝辛": {"components": ["帝", "辛"], "meaning": "帝辛（纣王）"},
}


def get_char_category(char):
    """获取字符所属类别"""
    if char in ORACLE_RADICALS:
        return ORACLE_RADICALS[char].get("category", "其他")
    return "未知"


def get_similar_chars(char, max_count=5):
    """获取形近字"""
    if char in SIMILAR_CHARS:
        return SIMILAR_CHARS[char][:max_count]
    return []


def guess_meaning_from_context(nearby_chars=None):
    """
    根据上下文推测可能的语义类别
    
    Args:
        nearby_chars: 前后相邻的已识别字符列表
        
    Returns:
        list: 可能的语境类别列表
    """
    if not nearby_chars:
        return []
    
    context_scores = {}
    for ctx_name, ctx_chars in DIVINATION_CONTEXTS.items():
        score = sum(1 for c in nearby_chars if c in ctx_chars)
        if score > 0:
            context_scores[ctx_name] = score
    
    # 返回最可能的语境
    sorted_ctx = sorted(context_scores.items(), key=lambda x: x[1], reverse=True)
    return [ctx[0] for ctx in sorted_ctx[:3]]


def analyze_ambiguous_character(predicted_char, confidence, top_predictions, 
                                  pollution_level=None, nearby_chars=None):
    """
    对难以定义的字符进行大致意思揣摩
    
    Args:
        predicted_char: 模型预测的top1字符
        confidence: 置信度 (0-1)
        top_predictions: top-k预测列表 [{"char":..., "prob":...}, ...]
        pollution_level: 污染程度评估
        nearby_chars: 上下文相邻字符列表
        
    Returns:
        dict: 包含揣摩结果的字典
    """
    result = {
        "status": "ambiguous",
        "pollution_assessment": None,
        "possible_categories": [],
        "radical_analysis": [],
        "similar_chars": [],
        "context_hints": [],
        "hewen_possibility": None,
        "rough_meaning": "",
        "confidence_level": "",
        "suggestions": [],
        "reasoning": ""
    }
    
    # 1. 评估污染/疑难程度
    if confidence < 0.2:
        result["pollution_assessment"] = POLLUTION_FEATURES["严重污染"]
        result["confidence_level"] = "极低"
    elif confidence < 0.35:
        result["pollution_assessment"] = POLLUTION_FEATURES["中度污染"]
        result["confidence_level"] = "较低"
    else:
        result["pollution_assessment"] = POLLUTION_FEATURES["难以定义"]
        result["confidence_level"] = "中等偏低"
    
    # 2. 部首/形符分析
    top_chars = [p["char"] for p in top_predictions[:3] if p["char"] in ORACLE_RADICALS]
    for char in top_chars:
        rad_info = ORACLE_RADICALS[char].copy()
        rad_info["name"] = char
        result["radical_analysis"].append(rad_info)
        result["possible_categories"].append(rad_info["category"])
    
    # 去重类别
    result["possible_categories"] = list(set(result["possible_categories"]))
    
    # 3. 形近字分析
    for pred in top_predictions[:3]:
        sims = get_similar_chars(pred["char"])
        if sims:
            result["similar_chars"].extend(sims)
    result["similar_chars"] = list(set(result["similar_chars"]))[:8]
    
    # 4. 上下文语境推断
    if nearby_chars:
        contexts = guess_meaning_from_context(nearby_chars)
        result["context_hints"] = contexts
    
    # 5. 合文可能性检查
    if len(top_predictions) >= 2 and top_predictions[0]["prob"] < 40:
        possible_hewen = []
        top_char_set = set(p["char"] for p in top_predictions[:5])
        for hewen_name, hewen_info in HEWEN_PATTERNS.items():
            match_count = sum(1 for c in hewen_info["components"] if c in top_char_set)
            if match_count >= 2:
                possible_hewen.append({
                    "name": hewen_name,
                    "meaning": hewen_info["meaning"],
                    "match": match_count
                })
        if possible_hewen:
            possible_hewen.sort(key=lambda x: x["match"], reverse=True)
            result["hewen_possibility"] = possible_hewen[:3]
    
    # 6. 综合揣摩大致意思
    meaning_parts = []
    
    # 基于部首
    if result["radical_analysis"]:
        rad = result["radical_analysis"][0]
        meaning_parts.append(
            f"从字形特征看，含「{rad['name']}」形，与「{rad['meaning']}」相关"
        )
    
    # 基于top预测
    if predicted_char and predicted_char != "?":
        meaning_parts.append(
            f"最接近已知字「{predicted_char}」（置信度{confidence:.1%}）"
        )
    
    # 基于形近字
    if result["similar_chars"]:
        meaning_parts.append(
            f"与「{'」「'.join(result['similar_chars'][:3])}」字形相近，可能是异体或通假"
        )
    
    # 基于语境
    if result["context_hints"]:
        ctx = result["context_hints"][0]
        ctx_examples = [c for c in DIVINATION_CONTEXTS.get(ctx, [])[:3]]
        meaning_parts.append(
            f"结合上下文，属「{ctx}」类卜辞的可能性较大"
        )
    
    # 基于合文
    if result["hewen_possibility"]:
        hw = result["hewen_possibility"][0]
        meaning_parts.append(
            f"字形紧凑，不排除是「{hw['name']}」合文（释为「{hw['meaning']}」）"
        )
    
    # 基于污染
    if confidence < 0.3:
        meaning_parts.append("但图像污损较严重，以上揣摩仅供参考")
    
    result["rough_meaning"] = "；".join(meaning_parts) if meaning_parts else "字形特征不明显，难以准确揣摩，建议人工鉴定"
    
    # 7. 建议
    result["suggestions"] = [
        "建议比对同一时期其他拓片中的相同字形",
        "结合前后文内容综合判断",
        "如有条件，参考甲骨文字编和相关研究文献",
        "低置信度结果建议由古文字专家审定"
    ]
    
    if confidence < 0.3:
        result["suggestions"].insert(0, "图像质量较差，建议使用更清晰的拓片图像")
    
    if result["hewen_possibility"]:
        result["suggestions"].insert(0, "注意是否为合文（多字合写）现象")
    
    # 8. 推理过程
    reasoning_parts = [
        f"模型预测top1为「{predicted_char}」，置信度{confidence:.1%}",
        f"Top-5预测: {[p['char'] for p in top_predictions[:5]]}",
    ]
    if result["pollution_assessment"]:
        reasoning_parts.append(f"污染评估: {result['pollution_assessment']['description']}")
    if result["possible_categories"]:
        reasoning_parts.append(f"可能类别: {', '.join(result['possible_categories'])}")
    
    result["reasoning"] = "；".join(reasoning_parts)
    
    return result


def generate_explanation(ambiguous_result):
    """生成人性化的解释文本"""
    lines = []
    
    lines.append("【字符分析报告】")
    lines.append(f"置信度等级: {ambiguous_result['confidence_level']}")
    lines.append("")
    
    if ambiguous_result["pollution_assessment"]:
        pa = ambiguous_result["pollution_assessment"]
        lines.append(f"▶ 图像评估: {pa['description']}")
    
    lines.append("")
    lines.append("▶ 大致意思揣摩:")
    lines.append(f"  {ambiguous_result['rough_meaning']}")
    
    if ambiguous_result["radical_analysis"]:
        lines.append("")
        lines.append("▶ 部首/形符分析:")
        for rad in ambiguous_result["radical_analysis"][:3]:
            lines.append(f"  • 「{rad['name']}」: {rad['meaning']}（{rad['category']}类）")
    
    if ambiguous_result["similar_chars"]:
        lines.append("")
        lines.append("▶ 形近字参考:")
        lines.append(f"  「{'」「'.join(ambiguous_result['similar_chars'][:5])}」")
    
    if ambiguous_result["context_hints"]:
        lines.append("")
        lines.append("▶ 语境提示:")
        for ctx in ambiguous_result["context_hints"]:
            lines.append(f"  • {ctx}类卜辞")
    
    if ambiguous_result["hewen_possibility"]:
        lines.append("")
        lines.append("▶ 合文可能性:")
        for hw in ambiguous_result["hewen_possibility"]:
            lines.append(f"  • 「{hw['name']}」→ 释为「{hw['meaning']}」")
    
    lines.append("")
    lines.append("▶ 建议:")
    for s in ambiguous_result["suggestions"][:4]:
        lines.append(f"  • {s}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print("甲骨文知识库测试")
    print("=" * 50)
    print(f"部首/形符数量: {len(ORACLE_RADICALS)}")
    print(f"形近字分组数量: {len(SIMILAR_CHARS)}")
    print(f"卜辞语境分类: {list(DIVINATION_CONTEXTS.keys())}")
    print(f"合文模式数量: {len(HEWEN_PATTERNS)}")
    
    # 模拟一个难以定义的字
    test_top_preds = [
        {"char": "日", "prob": 25.3},
        {"char": "口", "prob": 18.7},
        {"char": "曰", "prob": 12.1},
        {"char": "白", "prob": 8.5},
        {"char": "田", "prob": 6.2},
    ]
    
    result = analyze_ambiguous_character(
        predicted_char="日",
        confidence=0.25,
        top_predictions=test_top_preds,
        nearby_chars=["癸", "卯", "卜", "贞", "雨"]
    )
    
    print("\n" + "=" * 50)
    print(generate_explanation(result))
