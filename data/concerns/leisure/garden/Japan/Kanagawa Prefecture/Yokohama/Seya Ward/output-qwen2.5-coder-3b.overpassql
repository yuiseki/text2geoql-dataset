[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:ja"="横浜市"]->.inner;
(
  nwr["leisure"~"garden"](area.inner)(area.outer);
);
out geom;
