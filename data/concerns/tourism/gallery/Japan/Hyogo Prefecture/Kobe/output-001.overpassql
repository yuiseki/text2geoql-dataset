[out:json][timeout:30000];
area["name:en"="Hyogo Prefecture"]->.outer;
area["name:en"="Kobe"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
