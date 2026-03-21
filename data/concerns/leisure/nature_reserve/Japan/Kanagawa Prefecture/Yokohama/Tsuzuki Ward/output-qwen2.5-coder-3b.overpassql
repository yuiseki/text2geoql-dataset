[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["leisure"~"nature_reserve"](area.inner)(area.outer);
);
out geom;
