[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
area["name:zh"="香港"][boundary=administrative]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
