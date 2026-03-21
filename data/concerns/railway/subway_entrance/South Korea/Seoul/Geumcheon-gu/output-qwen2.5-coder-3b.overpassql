[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Geumcheon-gu"]->.inner;
(
  nwr["railway"="subway"](area.inner)(area.outer);
);
out geom;
