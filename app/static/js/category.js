(function(global) {
    var game_options = [{
        pk: 3,
        name: '休闲益智'
    }, {
        pk: 4,
        name: '角色冒险'
    }, {
        pk: 5,
        name: '动作格斗'
    }, {
        pk: 6,
        name: '策略游戏'
    }, {
        pk: 7,
        name: '体育竞技'
    }, {
        pk: 8,
        name: '飞行射击'
    }, {
        pk: 9,
        name: '卡片棋牌'
    }, {
        pk: 10,
        name: '经营养成'
    }, {
        pk: 11,
        name: '其他游戏'
    }];

    var soft_options = [{
        pk: 12,
        name: '系统安全'
    }, {
        pk: 13,
        name: '壁纸美化'
    }, {
        pk: 14,
        name: '聊天通讯'
    }, {
        pk: 15,
        name: '生活实用'
    }, {
        pk: 16,
        name: '书籍阅读'
    }, {
        pk: 17,
        name: '影音图像'
    }, {
        pk: 18,
        name: '学习办公'
    }, {
        pk: 19,
        name: '网络社区'
    }, {
        pk: 20,
        name: '地图导购'
    }, {
        pk: 21,
        name: '理财购物'
    }, {
        pk: 22,
        name: '其他软件'
    }];

    global.categories = {
        game_options: game_options,
        soft_options: soft_options,
        getParentPk: function(pk) {
            return pk < 12 ? 2 : 1;
        },
        getOptionsByParentPk: function(parentPk) {
            return parentPk == 1 ? soft_options : game_options;
        }
    };
})(window);
