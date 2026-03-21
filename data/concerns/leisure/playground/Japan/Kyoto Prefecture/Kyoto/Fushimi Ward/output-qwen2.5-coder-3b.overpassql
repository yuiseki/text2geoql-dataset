[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["leisure"~"playground"](area.inner)(area.outer);
);
out geom;
