[out:json][timeout:30];
area["name:ja"="東京都"]->.outer;
area["name:en"="Tokyo"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
