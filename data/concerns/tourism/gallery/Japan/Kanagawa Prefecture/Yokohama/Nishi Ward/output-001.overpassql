[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
