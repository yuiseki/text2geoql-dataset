[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  nwr["leisure"~"horse_riding"](area.inner)(area.outer);
);
out geom;
