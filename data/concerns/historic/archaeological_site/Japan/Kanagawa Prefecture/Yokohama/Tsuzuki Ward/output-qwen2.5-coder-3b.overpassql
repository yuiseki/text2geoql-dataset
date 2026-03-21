[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:ja"="横浜市"]->.inner;
(
  nwr["historic"~"archaeological"](area.inner)(area.outer);
);
out geom;
