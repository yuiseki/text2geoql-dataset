[out:json][timeout:30];
area["name:en"="Mizuho Ward"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["leisure"~"stadium"](area.inner)(area.outer);
);
out geom;
