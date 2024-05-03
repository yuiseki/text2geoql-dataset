[out:json][timeout:30000];
area["name:en"="Hong Kong"]->.outer;
area["name:en"="Kowloon City District"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
