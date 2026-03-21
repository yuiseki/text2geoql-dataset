[out:json][timeout:30];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:ja"="京都府"]->.inner;
(
  nwr["leisure"="fishing"](area.inner)(area.outer);
);
out geom;
