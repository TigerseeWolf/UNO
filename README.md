# UNO.py
UNO卡牌游戏类 -- 接入 QQ bot 使用
脚本包含三个类
```python
class Card
class Player
class UNO
```
## 添加游戏玩家
```python
from UNO import Player, UNO
uno = UNO()
player = Player(qq='1', name='张三')
uno.player_add_func(player)
```
## 删除游戏玩家
```python
uno.player_quit_func(player)
```
## 游戏运行使用gennerator
```python
uno_generator = uno.run()
for ret in uno_generator:
    print(ret[0])
    if uno.msg_in_flag:
        msg = input()
        uno_generator.send(msg)
        uno.msg_in_flag = False   # 每次输入完成需要手动复位标志位与玩家类
        uno.msg_in_player = None   # 这个是与QQbot结合的
```


# 附：游戏规则（稍稍改了下）
UNO游戏脚本（强制出牌、无叠牌、无质疑、不限时）  
卡牌说明：每副UNO牌包括：108张牌（76张数字牌，32张特殊牌）。  
一、数字牌共有10种（0、1、2、3、4、5、6、7、8、9），每种4个颜色（红、蓝、黄、绿），每种颜色0号1张、其余各2张，共计76张  
二、普通功能牌同样有四种颜色（红、蓝、黄、绿），有以下3种：  
>1、+2牌（每种颜色2张，共8张）  
>>当打出这张牌时，出牌者的下一个玩家必须罚抽2张牌，并且停止出牌一次。  
>>如果这张牌作为引导牌被翻开，则第一位出牌者必须罚抽2张牌（但可以正常出牌）；  
>
>2、反转牌（每种颜色2张，共8张）  
>>这张牌将会改变出牌的顺序。出牌顺序自顺时针方向改为逆时针方向；逆时针方向改为顺时针方向。  
>>如果这张牌作为引导牌被翻开，则第二位出牌者将改为右边那位，出牌顺序自顺时针方向改为逆时针方向。二人局中，此牌当做阻挡牌用； 
>
>3、阻挡牌（每种颜色2张，共8张）  
>>这张牌的出现将使出牌者的下家停止出牌一次。如果这张牌作为引导牌被翻开，则第一位出牌者将被直接停止出牌一次，由第二位开始出牌。  
  
三、高级功能牌牌面为黑色，有以下2种  
>1、黑牌（4张）  
>>当这张牌出现时，玩家可以指定接下来要出的牌的颜色（也可以不改）并继续游戏。  
>>玩家可以无视底牌打出这张【黑牌】，即使玩家手中有其他可出的牌。这张牌不能作为最后一张手牌打出。  
>>如果这张牌在一开始就被翻开，则由发牌者左边的第一位玩家来决定接下来要出的颜色；  
>2、黑牌+4（4张）  
>>这张牌可以无视底牌打出，并指定接下来要打出的牌的颜色，并且要求出牌者的下家自【牌库】中抽4张牌，停止出牌一次。  
>>只能在出牌者手上没有与底牌相同颜色的牌时打出这张牌。  
>>这张牌不能作为最后一张手牌打出。  
>>如果这张牌作为引导牌被翻开，则将这张牌放回、洗牌，重新翻一张牌。  
  
游戏顺序：  
1、每人发7张手牌，手牌分最高的作为第一位出牌者开始，初始出牌顺序为顺时针方向。  
2、翻开牌库顶第一张作为引导牌，第一名玩家根据引导牌出牌，然后玩家打出的牌依次成为底牌。  
3、基本行为：  
>（1）出牌  
>>打出与底牌同样颜色或图标（数字、功能）的牌；  
>（2）抽牌  
>>无牌可出（1张）或被惩罚（牌面或规则指定）时，从牌库中抽取相应张数；  
>（3）补出  
>>无牌可出时抽到的牌如果可以打出，则可以立即打出，只能补出抽到的牌，不能从原有手牌中补出牌；  
>(4）弃牌回收  
>>牌库透支（用尽）时，将底牌留在场上，其余牌洗切作为新的牌库。  
  
胜利条件：玩家手牌清空
