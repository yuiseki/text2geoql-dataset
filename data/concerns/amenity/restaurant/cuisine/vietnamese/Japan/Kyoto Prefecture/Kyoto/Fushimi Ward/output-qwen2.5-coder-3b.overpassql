[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["cuisine"~"vietnamese"](area.inner)(area.outer);
);
out geom;
