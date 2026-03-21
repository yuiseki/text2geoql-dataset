[out:json][timeout:30];
area["name:en"="Asahi Ward"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["leisure"~"playground"](area.inner)(area.outer);
);
out geom;
