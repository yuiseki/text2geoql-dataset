[out:json][timeout:30];
area["name:en"="Kanagawa Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["leisure"~"sports_centre"](area.inner)(area.outer);
);
out geom;
