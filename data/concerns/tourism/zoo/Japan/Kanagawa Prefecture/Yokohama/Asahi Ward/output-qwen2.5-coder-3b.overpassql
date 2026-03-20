[out:json][timeout:30];
area["name:ja"="横浜市"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
