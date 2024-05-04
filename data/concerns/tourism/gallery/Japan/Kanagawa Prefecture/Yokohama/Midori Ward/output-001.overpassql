[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Midori Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
