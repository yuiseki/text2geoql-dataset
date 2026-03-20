[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
area["name:en"="North District"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
