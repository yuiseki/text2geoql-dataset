[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Aichi Prefecture"]->.inner;
(
  nwr["building"~"library"](area.inner)(area.outer);
);
out geom;
