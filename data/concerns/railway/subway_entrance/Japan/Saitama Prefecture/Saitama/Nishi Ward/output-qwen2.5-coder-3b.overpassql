[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["railway"~"subway"](area.inner)(area.outer);
);
out geom;
