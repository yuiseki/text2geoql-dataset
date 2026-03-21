[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["leisure"~"horse_riding"](area.outer);
);
out geom;
