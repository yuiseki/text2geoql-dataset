[out:json][timeout:30];
area["name:ja"="東京都"]->.outer;
area["name:ja"="千代田区"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
