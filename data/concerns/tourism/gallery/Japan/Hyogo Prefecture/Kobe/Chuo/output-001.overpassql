[out:json][timeout:30000];
area["name:en"="Kobe"]->.outer;
area["name:en"="Chuo"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
