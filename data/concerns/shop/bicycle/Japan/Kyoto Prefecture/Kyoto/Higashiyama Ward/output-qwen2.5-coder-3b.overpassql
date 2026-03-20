[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:ja"~"京都"]->.inner;
(
  nwr["shop"~"bicycle"](area.inner)(area.outer);
);
out geom;
