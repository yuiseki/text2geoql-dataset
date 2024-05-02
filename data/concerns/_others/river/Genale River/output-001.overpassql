[out:json][timeout:30000];
area["name:en"="Ethiopia"]->.outer;
area["name:en"="Somali Region"]->.inner;
(
  nwr["name:en"="Genale river"](area.inner)(area.outer);
);
out geom;
