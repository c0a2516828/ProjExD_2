
import os
import sys
import time
import pygame as pg
import random

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool,bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル(横方向結果判定、縦方向結果判定)
    画面内ならTrue、画面外ならFalseを返す
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に、半透明の黒い画面を被せ、
    「Game Over」の文字と泣いているこうかとんを表示する関数
    引数 screen: 描画先の画面Surface
    戻り値: なし
    """

    bg_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(bg_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))

    bg_img.set_alpha(200)

    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2
    bg_img.blit(txt, txt_rct)

    kk_img = pg.image.load("fig/8.png")
    kk_rct1 = kk_img.get_rect()
    kk_rct1.center = WIDTH // 2 - 200, HEIGHT // 2
    bg_img.blit(kk_img, kk_rct1)

    kk_rct2 = kk_img.get_rect()
    kk_rct2.center = WIDTH // 2 + 200, HEIGHT // 2
    bg_img.blit(kk_img, kk_rct2)

    screen.blit(bg_img, [0, 0])

    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素とするリストと、加速度リストを返す関数
    戻り値: (爆弾Surfaceのリスト, 加速度のリスト)
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応するこうかとん画像Surfaceの辞書を返す関数
    戻り値: 移動量タプルをキー、画像Surfaceを値とした辞書
    """
    img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img_flip = pg.transform.flip(img, True, False)  # 右向き
    
    return {
        (0, 0): img_flip,                                     # キー押下なし（デフォルト右）
        (0, -5): pg.transform.rotozoom(img_flip, 90, 1.0),    # 上
        (+5, -5): pg.transform.rotozoom(img_flip, 45, 1.0),   # 右上
        (+5, 0): img_flip,                                    # 右
        (+5, +5): pg.transform.rotozoom(img_flip, -45, 1.0),  # 右下
        (0, +5): pg.transform.rotozoom(img_flip, -90, 1.0),   # 下
        (-5, +5): pg.transform.rotozoom(img, 45, 1.0),   # 左下
        (-5, 0): img,                                    # 左
        (-5, -5): pg.transform.rotozoom(img, -45, 1.0),  # 左上
    }

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0,0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0,WIDTH), random.randint(0,HEIGHT)
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_speed = 1.0 + (min(tmr // 500,9)*0.5) #移動速度の設定
        move_x = sum_mv[0] * kk_speed #移動速度を適用
        move_y = sum_mv[1] * kk_speed
        kk_rct.move_ip(move_x,move_y) #移動の実行
 
        if check_bound(kk_rct) != (True,True):
            kk_rct.move_ip(-move_x,-move_y)
        kk_img = kk_imgs[tuple(sum_mv)] #移動方向にあった画像の選択
        screen.blit(kk_img, kk_rct)

        bb_img = bb_imgs[min(tmr // 500, 9)] #段階に応じた爆弾画像の選択
        bb_rct.width = bb_img.get_rect().width #爆弾RectのサイズをSurfaceに合わせる
        bb_rct.height = bb_img.get_rect().height
        avx = vx * bb_accs[min(tmr // 500, 9)] #段階に応じた横速度
        avy = vy * bb_accs[min(tmr // 500, 9)] #段階に応じた縦速度

        bb_rct.move_ip(avx,avy) #速度に応じて爆弾を移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:#画面外に出たら移動方向を反転させる
            vx*=-1
        if not tate:
            vy*=-1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
