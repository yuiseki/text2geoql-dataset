[out:json][timeout:30];
area["name:en"="Longhua District"][boundary=administrative]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
