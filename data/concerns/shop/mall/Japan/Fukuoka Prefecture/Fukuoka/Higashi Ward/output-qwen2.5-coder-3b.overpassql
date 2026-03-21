[out:json][timeout:30];
area["name:ja"="福岡県"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
