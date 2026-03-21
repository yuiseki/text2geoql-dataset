[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:ja"="東京都"]->.inner;
(
  nwr["embassy"](area.inner)(area.outer);
);
out geom;
