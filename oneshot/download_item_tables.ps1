for ($i=1; $i -lt 81; $i++){ 
    $num = "{0:00}" -f $i
#    curl http://japan-mk.blog.jp/mk8dx.info-4/icon/$num.png -o item_tables/$num.png
    curl http://japan-mk.blog.jp/mk8dx.info-4/icon/${num}_1.png -o item_tables/${num}_1.png
    curl http://japan-mk.blog.jp/mk8dx.info-4/icon/${num}_2.png -o item_tables/${num}_2.png
    curl http://japan-mk.blog.jp/mk8dx.info-4/icon/${num}_3.png -o item_tables/${num}_3.png
}