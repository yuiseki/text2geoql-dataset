[out:json][timeout:30];
area["name:ja"="京都府"]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["building"="castle"](area.inner)(area.outer);
);
out geom;
