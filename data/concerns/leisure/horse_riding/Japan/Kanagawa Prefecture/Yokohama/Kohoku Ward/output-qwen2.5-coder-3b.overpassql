[out:json][timeout:30];
area["name:en"="Kohoku Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["leisure"~"horse_riding"](area.inner)(area.outer);
);
out geom;
