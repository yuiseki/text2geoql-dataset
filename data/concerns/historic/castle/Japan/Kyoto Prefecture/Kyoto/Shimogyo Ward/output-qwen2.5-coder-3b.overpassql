[out:json][timeout:30];
area["name:ja"="京都府"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["building"="castle"](area.inner)(area.outer);
);
out geom;
