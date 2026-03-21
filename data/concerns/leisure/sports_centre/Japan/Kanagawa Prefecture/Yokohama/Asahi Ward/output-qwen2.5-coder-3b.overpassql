[out:json][timeout:30];
area["name:en"="Asahi Ward"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["leisure"~"sports_centre"](area.inner)(area.outer);
);
out geom;
