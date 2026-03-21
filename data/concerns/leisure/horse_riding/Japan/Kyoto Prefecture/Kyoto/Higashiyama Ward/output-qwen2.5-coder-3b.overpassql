[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:ja"~"京都"]->.inner;
(
  nwr["leisure"~"horse_riding"](area.inner)(area.outer);
);
out geom;
