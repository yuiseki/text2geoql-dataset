[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["cuisine"~"mexican"](area.inner)(area.outer);
);
out geom;
