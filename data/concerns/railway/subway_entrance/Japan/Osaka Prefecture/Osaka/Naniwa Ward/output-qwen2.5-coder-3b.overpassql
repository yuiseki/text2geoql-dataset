[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Naniwa Ward"]->.inner;
(
  nwr["railway"~"subway"](area.inner)(area.outer);
);
out geom;
