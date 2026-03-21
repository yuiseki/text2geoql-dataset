[out:json][timeout:30];
area["name:ja"="福岡県"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["leisure"~"ice_rink"](area.inner)(area.outer);
);
out geom;
