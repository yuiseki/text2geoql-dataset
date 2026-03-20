[out:json][timeout:30];
area["name:zh"="深圳市"][boundary=administrative]->.outer;
area["name:zh"="广东省"][boundary=administrative]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
