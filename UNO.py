"""
    UNO游戏脚本（强制出牌、无叠牌、无质疑、不限时）
卡牌说明：每副UNO牌包括：108张牌（76张数字牌，32张特殊牌）。
一、数字牌共有10种（0、1、2、3、4、5、6、7、8、9），每种4个颜色（红、蓝、黄、绿），每种颜色0号1张、其余各2张，共计76张
二、普通功能牌同样有四种颜色（红、蓝、黄、绿），有以下3种：
    1、+2牌（每种颜色2张，共8张）
        当打出这张牌时，出牌者的下一个玩家必须罚抽2张牌，并且停止出牌一次。
        如果这张牌作为引导牌被翻开，则第一位出牌者必须罚抽2张牌（但可以正常出牌）；
    2、反转牌（每种颜色2张，共8张）
        这张牌将会改变出牌的顺序。出牌顺序自顺时针方向改为逆时针方向；逆时针方向改为顺时针方向。
        如果这张牌作为引导牌被翻开，则第二位出牌者将改为右边那位，出牌顺序自顺时针方向改为逆时针方向。二人局中，此牌当做阻挡牌用；
    3、阻挡牌（每种颜色2张，共8张）
        这张牌的出现将使出牌者的下家停止出牌一次。如果这张牌作为引导牌被翻开，则第一位出牌者将被直接停止出牌一次，由第二位开始出牌。

三、高级功能牌牌面为黑色，有以下2种
    1、黑牌（4张）
        当这张牌出现时，玩家可以指定接下来要出的牌的颜色（也可以不改）并继续游戏。
        玩家可以无视底牌打出这张【黑牌】，即使玩家手中有其他可出的牌。这张牌不能作为最后一张手牌打出。
        如果这张牌在一开始就被翻开，则由发牌者左边的第一位玩家来决定接下来要出的颜色；
    2、黑牌+4（4张）
        这张牌可以无视底牌打出，并指定接下来要打出的牌的颜色，并且要求出牌者的下家自【牌库】中抽4张牌，停止出牌一次。
        只能在出牌者手上没有与底牌相同颜色的牌时打出这张牌。
        这张牌不能作为最后一张手牌打出。
        如果这张牌作为引导牌被翻开，则将这张牌放回、洗牌，重新翻一张牌。
        注意：玩家依然可以打出黑牌+4，即使他手上有与底牌相同颜色的牌。

游戏顺序：
    1、每人发7张手牌，手牌分最高的作为第一位出牌者开始，初始出牌顺序为顺时针方向。
    2、翻开牌库顶第一张作为引导牌，第一名玩家根据引导牌出牌，然后玩家打出的牌依次成为底牌。
    3、基本行为：
    （1）出牌
        打出与底牌同样颜色或图标（数字、功能）的牌；
    （2）抽牌
        无牌可出（1张）或被惩罚（牌面或规则指定）时，从牌库中抽取相应张数；
    （3）补出
        无牌可出时抽到的牌如果可以打出，则可以立即打出，只能补出抽到的牌，不能从原有手牌中补出牌；
    （4）宣言UNO
        打出倒数第2张手牌时，需要宣言【UNO】，表示只剩1张手牌；
    （5）质疑UNO
        当有人忘记宣言【UNO】时，所有其他玩家可在下一张牌被打出之前指明，此时被指明的玩家罚抽牌2张；
    （6）弃牌回收
        牌库透支（用尽）时，将底牌留在场上，其余牌洗切作为新的牌库。

胜利条件：玩家手牌清空
"""
import random


class Card:
    """
    卡牌类：记录卡牌的花色、数字、类型
    """
    def __init__(self, color='', number='', type_name=''):
        self.color = color      # 包括'R'|'Y'|'B'|'G'('红'|'黄'|'蓝'|'绿')4种类型，如果为行动卡中的+4和wild，则为空，打出时需要说变换的颜色
        self.number = number    # '0'~'9'，如果为行动卡则为空
        self.type = type_name   # 'normal'/'+2'/'reverse'/'skip'/'wild'/'wild+4'


class Player:
    """
    玩家类：记录玩家的数据
    """
    def __init__(self, group='', qq='', name=''):
        self.group = group
        self.qq = qq
        self.name = name
        self.card_list = []


class UNO:
    """
    游戏类
    """
    def __init__(self):
        self.player_list = []           # 存放所有玩家信息(如果退出游戏则会从列表中删除)
        self.all_player = []            # 存放所有玩家信息(不管有没有退出)
        self.order = 1                  # 为1时为出牌顺序往后，-1时为出牌顺序往前
        self.card_list = []             # 剩余牌堆
        self.discard_list = []          # 弃牌堆
        self.lead_card = Card()         # 引导牌
        self.num_player_now = -1        # 当前出牌玩家
        self.forbidden_flag = False     # 禁手标志
        self.card_effect_flag = False   # 卡牌效果标志
        self.begin_flag = False         # 游戏开始标志
        self.end_flag = False           # 游戏结束标志
        self.player_quit_flag = False   # 有玩家退出标志
        self.player_quit = None         # 有玩家退出标志
        self.generator = None           # 生成器，存放生成器用的
        self.msg_in_flag = False        # 需要外部输入信息标志
        self.msg_in_player = None       # 需要哪个玩家来输入
        self.room_id = ''               # 存放该游戏房间的ID号
        self.rule = '底牌为108张，规则强制出牌，无叠牌，无质疑，不限时。' \
                    '每个玩家根据上一家打出的卡牌，选择相同的颜色、数字或类型的卡牌进行打出，' \
                    '其中+4变色或变色为百搭型的卡牌，打出时需要指定颜色。' \
                    '且+4转色不能当作最后一张手牌打出。当有玩家手牌数量为0时，则获得胜利'

    def draw(self, player: Player) -> Card:
        """
        抽牌函数，随机从牌堆中抽取1张卡牌，置入玩家手牌
        :param player: 玩家，Player类
        :return: Card: 返回玩家抽到的牌
        """
        # 如果牌库空了，则把弃牌堆重新洗牌赋给牌堆
        if len(self.card_list) == 0:
            self.card_list = self.discard_list[:]
            self.discard_list = []
        # 如果牌库还是为空的话，则再加一副牌进入,应该不会出现吧= =
        if len(self.card_list) == 0:
            self.init_card()

        card_rand = random.randint(0, len(self.card_list) - 1)      # 随机牌堆抽牌
        card_draw = self.card_list[card_rand]                       # 抽到的牌
        player.card_list.append(card_draw)                          # 置入玩家手牌
        del self.card_list[card_rand]                               # 从牌堆中删除卡牌
        return card_draw

    def play(self, player: Player, card: Card):
        """
        玩家player从手牌中打出卡牌card
        加入弃牌堆中，从手牌中移除
        :param player: 玩家，Player类
        :param card: 卡牌，Card类
        :return:Null
        """
        self.discard_list.append(card)
        player.card_list.remove(card)

    def player_add_func(self, player: Player):
        """
        玩家加入到游戏
        :param player: 玩家，Player类
        :return: Null
        """
        self.player_list.append(player)

    def player_quit_func(self, player: Player):
        """
        玩家退出，自行设计惩罚结果
        :param player: 玩家， Player类
        :return: None
        """
        # 把所有手牌加入到弃牌堆中
        for card in player.card_list:
            self.discard_list.append(card)
        self.player_quit_flag = True
        self.player_quit = player
        self.player_list.remove(player)

    def init_card(self):
        """
        初始化牌堆，共108张牌
        :return:
        """
        # 数字牌（0每色X1，1~9每色X2） 共76张
        for color in ['R', 'Y', 'B', 'G']:
            num = 0
            self.card_list.append(Card(number=str(num), color=color, type_name='normal'))
            for num in range(1, 10):
                self.card_list.append(Card(number=str(num), color=color, type_name='normal'))
                self.card_list.append(Card(number=str(num), color=color, type_name='normal'))
        # 功能牌（每色X2） 共24张
        for color in ['R', 'Y', 'B', 'G']:
            for type_name in ['+2', 'skip', 'reverse']:
                self.card_list.append(Card(number='', color=color, type_name=type_name))
                self.card_list.append(Card(number='', color=color, type_name=type_name))
        # 无色牌 高级功能牌 X4 共8张
        for type_name in ['wild+4', 'wild']:
            self.card_list.append(Card(number='', color='', type_name=type_name))
            self.card_list.append(Card(number='', color='', type_name=type_name))
            self.card_list.append(Card(number='', color='', type_name=type_name))
            self.card_list.append(Card(number='', color='', type_name=type_name))

        self.discard_list = []

    def detect(self, player: Player) -> list:
        """
        探测玩家手上可以打出的手牌
        :param player: 玩家，玩家类
        :return: 返回可以出手牌的列表
        """
        enable_card_list = []   # 可以打出牌的卡牌列表初始化
        flag_color = False
        # 探测每张手牌
        for card in player.card_list:
            # 如果由相同颜色，则加入可打出集合牌
            if card.color == self.lead_card.color:
                if card.color == self.lead_card.color:
                    enable_card_list.append(card)
                    flag_color = True           # 一个是否有同颜色牌的标志位，后面判断要用
            else:
                # 如果不是相同颜色的，则看数字和类型是否匹配
                # 数字牌(同数字的时候),这里和颜色分开是保证不重复添加两次
                if card.type == 'normal' and card.number == self.lead_card.number:
                    enable_card_list.append(card)
                # 功能牌
                if card.type in ['reverse', 'skip', '+2']:
                    # 相同类型
                    if card.type == self.lead_card.type:
                        enable_card_list.append(card)
            # 万能牌
            if card.type == 'wild':
                # 除了只剩下一张牌时，任何时刻都可以打出
                if len(player.card_list) != 1:
                    enable_card_list.append(card)
            if card.type == 'wild+4':
                # 手牌不是只剩下一张牌, 且没有颜色相同的牌
                if len(player.card_list) != 1 and flag_color is False:
                    enable_card_list.append(card)

        # 再判断 wild+4卡是否能出
        if flag_color is True:
            for card in enable_card_list:
                if card.type == 'wild+4':
                    enable_card_list.remove(card)

        return enable_card_list

    def card_list_to_str(self, card_list: list) -> str:
        """
        将卡牌列表转成字符串
        :param card_list: 列表，存放卡牌，List[Card]
        :return: 字符串，str
        """
        msg = ""
        for card_rand in range(0, len(card_list)):
            ch_color = ''
            ch_type = ''
            card = card_list[card_rand]
            if card.color == 'R':
                ch_color = '红'
            if card.color == 'Y':
                ch_color = '黄'
            if card.color == 'B':
                ch_color = '蓝'
            if card.color == 'G':
                ch_color = '绿'
            if card.type == "+2":
                ch_type = "+2"
            if card.type == "reverse":
                ch_type = "反转"
            if card.type == "skip":
                ch_type = "跳过"
            if card.type == "wild":
                ch_type = "变色"
            if card.type == "wild+4":
                ch_type = "变色+4"

            msg_card = f'\n[{card_rand+1}]{ch_color}{card.number}{ch_type}'
            msg = msg + msg_card
        return msg

    def card_function(self, player: Player, card: Card):
        """
        执行部分卡牌效果
        :param player: 玩家，Player类
        :param card: 卡牌， Card类
        :return:
        """
        if card.type == '+2':
            self.draw(player)
            self.draw(player)
        if card.type == 'wild+4':
            self.draw(player)
            self.draw(player)
            self.draw(player)
            self.draw(player)
            self.forbidden_flag = True
        if card.type == 'skip':
            self.forbidden_flag = True
        if card.type == 'reverse' and len(self.player_list) == 2:
            self.forbidden_flag = True

    def run(self):
        """
        运行游戏的主函数
        :return:
        """
        self.begin_flag = True
        # 1.初始化卡牌
        self.init_card()
        self.card_effect_flag = False
        msg = f'本次共有{len(self.player_list)}名玩家,分别为'
        for player in self.player_list:
            msg = msg + '\n' + player.name
        yield msg, None
        # 1.1 每个玩家分7张卡牌
        for player in self.player_list:
            for i in range(0, 7):
                self.draw(player)
            # 1.2 输出每个玩家的手牌信息
            yield f"玩家{player.name}的手牌为:{self.card_list_to_str(player.card_list)}", player

        # 1.3 决定哪个玩家最先出牌
        self.num_player_now = random.randint(0, len(self.player_list) - 1)
        player_now = self.player_list[self.num_player_now]

        # 2. 翻出引导牌
        random_num = random.randint(0, len(self.card_list)-1)
        self.lead_card = self.card_list[random_num]
        # 2.1 引导牌判断
        # 2.1.1 如果为wild+4，重新翻开引导牌
        while self.lead_card.type == 'wild+4':
            random_num = random.randint(0, len(self.card_list)-1)
            self.lead_card = self.card_list[random_num]

        # 2.1.2 如果为+2,则第一个玩家抽2张
        if self.lead_card.type == '+2':
            self.draw(player_now)
            self.draw(player_now)

        # 2.1.3 如果引导牌为反转，则改变顺序
        if self.lead_card.type == 'reverse':
            self.order = - self.order                            # 改变顺序

        # 2.1.4 如果引导牌为跳过，置为禁手标志
        if self.lead_card.type == 'skip':
            self.forbidden_flag = True                              # 禁手标志置True

        # 2.1.5 如果翻出的牌为变色，则由上一个玩家来决定是先出什么颜色
        if self.lead_card.type == 'wild':
            yield f'由玩家{self.player_list[self.num_player_now - 1].name}决定花色', None
            self.msg_in_flag = True
            self.msg_in_player = self.player_list[self.num_player_now - 1]
            self.lead_card.color = yield f'红输入R,黄输入Y,蓝输入B,绿输入G', self.player_list[self.num_player_now - 1]
            while self.lead_card.color not in ['R', 'G', 'B', 'Y']:
                self.msg_in_flag = True
                self.msg_in_player = self.player_list[self.num_player_now - 1]
                self.lead_card.color = yield f'红输入R,黄输入Y,蓝输入B,绿输入G', self.player_list[self.num_player_now - 1]

        self.discard_list.append(self.card_list[random_num])    # 进弃牌堆
        del self.card_list[random_num]                          # 出牌堆

        # 3.主体循环
        while self.end_flag is False:
            if self.player_quit_flag:
                yield f'玩家{self.player_quit.name}退出了游戏', None
            # 当前状态输出
            yield f'当前底牌为:{self.card_list_to_str([self.lead_card])}', None
            yield f'当前出牌玩家为:{player_now.name}', None
            # 对玩家执行卡牌效果，注意游戏一开始时，卡牌效果标志是False的
            if self.card_effect_flag is True:
                self.card_function(player_now, self.lead_card)  # 卡牌执行
                self.card_effect_flag = False
            # 3.1 判断是否被禁手, 对当前玩家执行引导牌功能
            if self.forbidden_flag is False:
                # 3.2 出牌阶段
                # 3.2.1 探测玩家是否有牌可以使用
                yield f"当前手牌：{self.card_list_to_str(player_now.card_list)}", player_now
                enable_card_list = self.detect(player_now)
                # 如果玩家有牌可以出
                if len(enable_card_list) != 0:
                    msg_ret = self.card_list_to_str(enable_card_list)

                    card_label = len(enable_card_list) + 1
                    while card_label > len(enable_card_list):
                        try:
                            self.msg_in_flag = True
                            self.msg_in_player = player_now
                            card_label = yield f'可以打出的手牌{msg_ret}\n请输入要出的相应卡牌编号(可以打出的手牌):', player_now
                            yield '', None
                            card_label = int(card_label)
                        except ValueError:
                            card_label = len(enable_card_list) + 1

                    # 3.2.2 玩家出牌
                    msg1 = self.card_list_to_str([enable_card_list[card_label - 1]])
                    yield f'玩家{player_now.name}打出了{msg1}', None

                    self.play(player_now, enable_card_list[card_label - 1])
                    self.lead_card = enable_card_list[card_label - 1]           # 变换lead_card
                    if self.lead_card.type == 'reverse':                        # reverse要立刻执行
                        self.order = - self.order
                        if len(self.player_list) == 2:                                  # 当人数为2人时，reverse牌等于skip牌
                            self.card_effect_flag = True                                # 激发卡牌效果标志
                    else:
                        self.card_effect_flag = True                                # 激发卡牌效果标志

                    # 3.2.3 判断玩家是否出完手牌
                    if len(player_now.card_list) == 0:
                        self.end_flag = True    # 游戏结束
                        break

                    # 3.2.4 判断玩家是否剩下一张牌
                    if len(player_now.card_list) == 1:
                        yield f'玩家：{player_now.name} UNO！！', None    # 玩家UNO了

                    # 3.2.5 如果玩家打出的是wild或wild+4
                    if self.lead_card.type == 'wild' or self.lead_card.type == 'wild+4':
                        yield f'正在由玩家:{player_now.name}决定花色...', None
                        self.msg_in_flag = True
                        self.msg_in_player = player_now
                        self.lead_card.color = yield f'红输入R,黄输入Y,蓝输入B,绿输入G', player_now
                        yield '', None
                        while self.lead_card.color not in ['R', 'G', 'B', 'Y']:
                            self.msg_in_flag = True
                            self.msg_in_player = player_now
                            self.lead_card.color = yield f'红输入R,黄输入Y,蓝输入B,绿输入G', player_now
                            yield '', None

                        yield f'玩家{player_now.name}决定颜色为{self.lead_card.color}', None
                else:
                    # 3.3 无牌可以出，需要抽牌
                    # 3.3.1 抽牌
                    card_draw = self.draw(player_now)
                    yield f'玩家{player_now.name}抽了1张牌', None
                    # 3.3.2 补出（强制补出）
                    # 3.3.2.1 抽到数字牌
                    if card_draw.type == 'normal':
                        # 相同数字
                        if card_draw.number == self.lead_card.number:
                            self.play(player_now, card_draw)
                            self.lead_card = card_draw         # 变换lead_card
                            yield f'玩家{player_now.name}强制补出了{self.card_list_to_str([card_draw])}', None
                            if len(player_now.card_list) == 1:
                                yield f'玩家：{player_now.name} UNO！！', None  # 玩家UNO了
                        else:
                            # 相同颜色
                            if card_draw.color == self.lead_card.color:
                                self.play(player_now, card_draw)
                                self.lead_card = card_draw         # 变换lead_card
                                yield f'玩家{player_now.name}强制补出了{self.card_list_to_str([card_draw])}', None
                                if len(player_now.card_list) == 1:
                                    yield f'玩家：{player_now.name} UNO！！', None  # 玩家UNO了
                    else:
                        # 3.3.2.2 抽到非数字但同颜色其他卡牌
                        if card_draw.color == self.lead_card.color:
                            self.play(player_now, card_draw)
                            self.lead_card = card_draw         # 变换lead_card
                            if self.lead_card.type == 'reverse':  # reverse要立刻执行
                                self.order = - self.order
                                if len(self.player_list) == 2:  # 当人数为2人时，reverse牌等于skip牌
                                    self.card_effect_flag = True  # 激发卡牌效果标志
                            else:
                                self.card_effect_flag = True  # 激发卡牌效果标志
                            yield f'玩家{player_now.name}强制补出了{self.card_list_to_str([card_draw])}', None
                            # 判断玩家是否剩下一张牌
                            if len(player_now.card_list) == 1:
                                yield f'玩家：{player_now.name} UNO！！', None  # 玩家UNO了
                        else:
                            # # 3.3.2.3 抽到非数字，且颜色不同的，但是类型相同功能卡，或者万能牌
                            if card_draw.type == self.lead_card.type or card_draw.type in ['wild', 'wild+4']:
                                self.play(player_now, card_draw)
                                self.lead_card = card_draw         # 变换lead_card
                                if self.lead_card.type == 'reverse':  # reverse要立刻执行
                                    self.order = - self.order
                                    if len(self.player_list) == 2:  # 当人数为2人时，reverse牌等于skip牌
                                        self.card_effect_flag = True  # 激发卡牌效果标志
                                else:
                                    self.card_effect_flag = True  # 激发卡牌效果标志

                                # 强制打出
                                yield f'玩家{player_now.name}强制补出了{self.card_list_to_str([self.lead_card])}', None
                                # 判断玩家是否剩下一张牌
                                if len(player_now.card_list) == 1:
                                    yield f'玩家：{player_now.name} UNO！！', None  # 玩家UNO了
                                # 如果打出变色，则再+4
                                if self.lead_card.type == 'wild' or self.lead_card.type == 'wild+4':
                                    yield f'正在由玩家:{player_now.name}决定花色...', None
                                    self.msg_in_flag = True
                                    self.msg_in_player = player_now
                                    self.lead_card.color = yield f'红输入R,黄输入Y,蓝输入B,绿输入G', player_now
                                    yield '',None
                                    while self.lead_card.color not in ['R', 'G', 'B', 'Y']:
                                        self.msg_in_flag = True
                                        self.msg_in_player = player_now
                                        self.lead_card.color = yield f'红输入R,黄输入Y,蓝输入B,绿输入G', player_now
                                        yield '', None

                                    yield f'玩家{player_now.name}决定颜色为{self.lead_card.color}', None
            else:
                # 禁手完成
                self.forbidden_flag = False     # 禁手标志复位
                self.card_effect_flag = False   # 卡牌效果执行完成，卡牌效果标志复位

            # 下一位玩家
            self.num_player_now = (self.num_player_now + self.order) % len(self.player_list)      # 下一位玩家编号计算
            player_now = self.player_list[self.num_player_now]   # 下一位玩家
        yield f'胜利者为:{player_now.name}', None
        yield '', player_now
        self.begin_flag = False


if __name__ == '__main__':
    uno = UNO()
    # 加入3名玩家
    player_1 = Player(qq='1', name='张三')
    uno.player_add_func(player_1)
    player_2 = Player(qq='2', name='李四')
    uno.player_add_func(player_2)
    player_3 = Player(qq='3', name='王五')
    uno.player_add_func(player_3)
    player_4 = Player(qq='4', name='赵六')
    uno.player_add_func(player_4)
    # 打印消息
    print(f'已加入{len(uno.player_list)}名玩家')
    print('游戏开始')
    # 游戏运行
    uno_generator = uno.run()
    # 这里用yield是便于与外部交互
    for ret in uno_generator:
        print(ret[0])
        if uno.msg_in_flag:
            msg = input()
            uno_generator.send(msg)
            uno.msg_in_flag = False
