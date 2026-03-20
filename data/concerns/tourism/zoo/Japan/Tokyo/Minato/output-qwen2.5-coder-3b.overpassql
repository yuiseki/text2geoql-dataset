[out:json][timeout:30];
area["name:ja"="港区"]->.outer;
area["name:en"="Minato"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
