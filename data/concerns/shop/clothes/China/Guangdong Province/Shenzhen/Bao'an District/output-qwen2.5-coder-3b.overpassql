[out:json][timeout:30];
area["name:zh"="宝安区"]->.outer;
area["name:zh"="深圳市"]->.inner;
(
  nwr["shop"~"clothes"](area.inner)(area.outer);
);
out geom;
