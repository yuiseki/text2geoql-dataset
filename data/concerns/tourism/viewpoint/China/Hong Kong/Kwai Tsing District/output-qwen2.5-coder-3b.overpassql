[out:json][timeout:30];
area["name:en"="Kwai Tsing District"][boundary=administrative]->.outer;
area["name:en"="Hong Kong"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
