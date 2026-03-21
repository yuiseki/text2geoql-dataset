[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["leisure"~"stadium"](area.inner)(area.outer);
);
out geom;
